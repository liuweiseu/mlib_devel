from .yellow_block import YellowBlock
from clk_factors import clk_factors
from constraints import ClockConstraint, ClockGroupConstraint, PortConstraint, RawConstraint


class rfsoc8x8(YellowBlock):
    def initialize(self):
        self.add_source('infrastructure/zcu216_clk_infrastructure.sv')
        self.add_source('utils/cdc_synchroniser.vhd')
        self.add_source('infrastructure/emio_gpio_iobuf.v')

        # create reference to block design name
        self.blkdesign = '{:s}_bd'.format(self.platform.conf['name'])

        self.pl_clk_mhz = self.blk['pl_clk_rate']
        self.T_pl_clk_ns = 1.0/self.pl_clk_mhz*1000

        self.provides.append('adc_clk')
        self.provides.append('adc_clk90')
        self.provides.append('adc_clk180')
        self.provides.append('adc_clk270')
        self.provides.append('adc_clk_rst')

        self.provides.append('sys_clk')
        self.provides.append('sys_rst')

        # TODO: is a bug that `axi4lite_interconnect` does not make a `requires` on `axil_clk`.
        # Looking into this more: the `_drc` check on YB requires/provides is done in `gen_periph_objs` but the `axi4lite_interconnect`
        # is not done until later within `generate_hdl > _instantiate_periphs`, therefore, by-passing any checks done.
        self.provides.append('axil_clk')    # from block design
        self.provides.append('axil_rst_n')  # from block desgin

        # rfsocs use the requires/provides for to check for `sysref` and `pl_sysref` for MTS
        self.provides.append('pl_sysref') # rfsoc platform/infrastructure provides so rfdc can require

        self.requires.append('M_AXI') # axi4lite interface from block design

        # PS EMIO GPIO width set by the rfsoc8x8_mpsoc presets, and the number of
        # its low bits that drive the LMK04828 control pins
        self.emio_gpio_width = 5
        self.lmk_ctrl_width = 4

    def modify_top(self, top):
        top.assign_signal('axil_clk', 'pl_sys_clk')
        #top.assign_signal('axil_rst', 'axil_rst')
        top.assign_signal('axil_rst_n', 'axil_arst_n') # TODO RENAME the board design one `axil_arst_n`
        top.assign_signal('sys_clk', 'pl_sys_clk')
        top.assign_signal('sys_rst', '~axil_arst_n')

        # generate clock parameters to use pl_clk to drive as the user IP clock
        # TODO: will need to make changes when other user ip clk source options provided
        clkparams = clk_factors(self.pl_clk_mhz, self.platform.user_clk_rate, vco_min=800.0, vco_max=1600.0)

        inst_infr = top.get_instance('zcu216_clk_infrastructure', 'zcu216_clk_infr_inst')
        inst_infr.add_parameter('PERIOD', "{:0.3f}".format(self.T_pl_clk_ns))
        inst_infr.add_parameter('MULTIPLY', clkparams[0])
        inst_infr.add_parameter('DIVIDE',   clkparams[1])
        inst_infr.add_parameter('DIVCLK',   clkparams[2])
        inst_infr.add_port('pl_clk_p',      "pl_clk_p", dir='in',  parent_port=True)
        inst_infr.add_port('pl_clk_n',      "pl_clk_n", dir='in',  parent_port=True)

        inst_infr.add_port('adc_clk', 'adc_clk')
        inst_infr.add_port('adc_clk90', 'adc_clk90')
        inst_infr.add_port('adc_clk180', 'adc_clk180')
        inst_infr.add_port('adc_clk270', 'adc_clk270')
        inst_infr.add_port('mmcm_locked', 'mmcm_locked', dir='out', parent_port=True)

        # LMK04828 SPI: PS SPI0 routed to EMIO (see the zynq_emio child). SCLK is
        # looped back into the PS as in the vendor reference design.
        top.add_port('lmk_spi_sclk', dir='out')
        top.add_port('lmk_spi_mosi', dir='out')
        top.add_port('lmk_spi_cs_n', dir='out')
        top.add_port('lmk_spi_miso', dir='in')
        top.assign_signal('lmk_spi_sclk', 'emio_spi0_sclk_o')
        top.assign_signal('emio_spi0_sclk_i', 'emio_spi0_sclk_o')
        top.assign_signal('lmk_spi_mosi', 'emio_spi0_m_o')
        top.assign_signal('emio_spi0_m_i', 'lmk_spi_miso')
        top.assign_signal('lmk_spi_cs_n', 'emio_spi0_ss_o_n')

        # LMK04828 control pins on PS GPIO EMIO bits 0-3 (REF_SEL0, REF_SEL1,
        # RESET, SYNC). EMIO GPIO bit 4 is not connected.
        n = self.lmk_ctrl_width
        iobuf = top.get_instance('emio_gpio_iobuf', 'lmk_ctrl_iobuf_inst')
        iobuf.add_parameter('WIDTH', n)
        iobuf.add_port('gpio_o', 'emio_gpio_tri_o[{:d}:0]'.format(n-1), parent_sig=False)
        iobuf.add_port('gpio_t', 'emio_gpio_tri_t[{:d}:0]'.format(n-1), parent_sig=False)
        iobuf.add_port('gpio_i', 'emio_gpio_tri_i[{:d}:0]'.format(n-1), parent_sig=False)
        iobuf.add_port('gpio_io', 'lmk_ctrl', dir='inout', width=n, parent_port=True)
        top.assign_signal('emio_gpio_tri_i[{:d}:{:d}]'.format(self.emio_gpio_width-1, n),
                          "{:d}'b0".format(self.emio_gpio_width-n))

    def gen_children(self):
        children = []
        # TODO: board_id 167 is provisional (160-162, 165, 166 are taken by the
        # other RFSoC boards); confirm it with the casperfpga board registry.
        children.append(YellowBlock.make_block({'fullpath': self.fullpath, 'tag': 'xps:sys_block', 'board_id': '167', 'rev_maj': '2', 'rev_min': '0', 'rev_rcs': '1'}, self.platform))

        # instance block design containing mpsoc, and axi protocol converter for casper
        # mermory map (HPM0)
        zynq_blk = {
            'tag'     : 'xps:zynq_usplus',
            'name'    : 'mpsoc',
            'presets' : 'rfsoc8x8_mpsoc',
            'maxi_0'  : {'conf': {'enable': 1, 'data_width': 32},  'intf': {'dest': 'axi_proto_conv/S_AXI'}},
            'maxi_1'  : {'conf': {'enable': 0, 'data_width': 128}, 'intf': {}},
            'maxi_2'  : {'conf': {'enable': 0, 'data_width': 128}, 'intf': {}}
            #'maxi_2'  : {'conf': {'enable': 1, 'data_width': 128}, 'intf': {'dest': 'M_AXI_0'}}
        }
        children.append(YellowBlock.make_block(zynq_blk, self.platform))

        proto_conv_blk = {
            'tag'             : 'xps:axi_protocol_converter',
            'name'            : 'axi_proto_conv',
            'saxi_intf'       : {'dest': 'mpsoc/M_AXI_HPM0_FPD'},
            'maxi_intf'       : {'dest': 'M_AXI'},
            'aruser_wid'      : 0,
            'awuser_wid'      : 0,
            'buser_wid'       : 0,
            'data_wid'        : 32,
            'id_wid'          : 16,
            'mi_protocol'     : 'AXI4LITE',
            'rw_mode'         : 'READ_WRITE',
            'ruser_wid'       : 0,
            'si_protocol'     : 'AXI4',
            'translation_mode': 2,
            'wuser_wid'       : 0
        }
        children.append(YellowBlock.make_block(proto_conv_blk, self.platform))

        # expose PS SPI0 and GPIO EMIO (LMK04828 programming and control). Must
        # come after the mpsoc child so its bd commands follow the presets.
        emio_blk = {
            'tag'       : 'xps:zynq_emio',
            'name'      : 'mpsoc_emio',
            'ps_cell'   : 'mpsoc',
            'spi'       : [0],
            'gpio_width': self.emio_gpio_width,
        }
        children.append(YellowBlock.make_block(emio_blk, self.platform))
        return children


    def gen_constraints(self):
        cons = []
        cons.append(ClockConstraint('pl_clk_p', 'pl_clk_p', period=self.T_pl_clk_ns, port_en=True, virtual_en=False))
        cons.append(PortConstraint('pl_clk_p', 'pl_clk_p'))

        cons.append(ClockGroupConstraint('clk_pl_0', 'pl_clk_mmcm', 'asynchronous'))

        # mmcm_locked drives GPIO 8 of the RFSoC8x8 board (AM5, HP bank 66, VCCO 1.2 V)
        cons.append(RawConstraint('set_property -dict { PACKAGE_PIN AM5 IOSTANDARD LVCMOS12 } [get_ports { mmcm_locked }]'))

        # LMK04828 SPI and control pins
        for port in ['lmk_spi_sclk', 'lmk_spi_mosi', 'lmk_spi_cs_n', 'lmk_spi_miso']:
            cons.append(PortConstraint(port, port))
        n = self.lmk_ctrl_width
        cons.append(PortConstraint('lmk_ctrl', 'lmk_ctrl', port_index=list(range(n)), iogroup_index=list(range(n))))

        return cons


    def gen_tcl_cmds(self):
        tcl_cmds = {}
        tcl_cmds['init'] = []
        tcl_cmds['create_bd'] = []
        tcl_cmds['pre_synth'] = []

        # export hardware design xsa for software
        tcl_cmds['post_bitgen'] = []
        # TODO: $xsa_file comes from the backends class. Could re-write the path here but $xsa_file exists, use it instead.
        # This then begs the question as to if there should be some sort of known tcl variables to check against
        tcl_cmds['post_bitgen'] += ['write_hw_platform -fixed -include_bit -force -file $xsa_file']

        return tcl_cmds
