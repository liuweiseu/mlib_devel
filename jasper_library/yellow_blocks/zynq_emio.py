from .yellow_block import YellowBlock

class zynq_emio(YellowBlock):
  """
  Expose MPSoC peripherals that are routed to EMIO as block design ports.

  The EMIO pins only exist on the PS cell once the platform presets (sourced by
  the `zynq_usplus` block's `modify_bd`) route the peripheral to EMIO. This block
  must therefore be generated after the `zynq_usplus` child in the platform's
  `gen_children` list so that its `modify_bd` commands follow the presets.

  Only the block design ports and the matching ports on the block design
  instance in `top` are created here. Connecting them to FPGA pins (IO buffers,
  pin constraints) is left to the platform yellow block.

  blk keys:
    ps_cell    : name of the PS cell in the block design (e.g. 'mpsoc')
    spi        : list of SPI controller indices to expose (e.g. [0])
    gpio_width : EMIO GPIO width to expose (0 to not expose GPIO). Must match
                 PSU__GPIO_EMIO_WIDTH of the PS presets.

  Top-level signals created (named after the block design ports):
    emio_spi<n>_sclk_o, emio_spi<n>_sclk_i, emio_spi<n>_m_o, emio_spi<n>_m_i,
    emio_spi<n>_ss_o_n
    emio_gpio_tri_o, emio_gpio_tri_t, emio_gpio_tri_i  ([gpio_width-1:0])
  """
  # (PS pin suffix, direction seen from the block design)
  spi_pins = [
    ('sclk_o', 'out'),
    ('sclk_i', 'in'),
    ('m_o',    'out'),
    ('m_i',    'in'),
    ('ss_o_n', 'out'),
  ]

  gpio_intf_port = 'emio_gpio'
  gpio_pins = ['tri_o', 'tri_t', 'tri_i']

  def initialize(self):
    self.ps_cell = self.blk['ps_cell']
    self.spi = list(self.blk.get('spi', []))
    self.gpio_width = int(self.blk.get('gpio_width', 0))

    self.blkdesign = '{:s}_bd'.format(self.platform.conf['name'])

  def spi_port_name(self, idx, pin):
    return 'emio_spi{:d}_{:s}'.format(idx, pin)

  def modify_bd(self, bd):
    for idx in self.spi:
      for pin, port_dir in self.spi_pins:
        port = self.spi_port_name(idx, pin)
        bd.add_port(port, port_dir)
        bd.add_raw_cmd('connect_bd_net [get_bd_pins {:s}/emio_spi{:d}_{:s}] [get_bd_ports {:s}]'.format(
          self.ps_cell, idx, pin, port))

    if self.gpio_width > 0:
      bd.add_raw_cmd('create_bd_intf_port -mode Master -vlnv xilinx.com:interface:gpio_rtl:1.0 {:s}'.format(
        self.gpio_intf_port))
      bd.add_raw_cmd('connect_bd_intf_net [get_bd_intf_pins {:s}/GPIO_0] [get_bd_intf_ports {:s}]'.format(
        self.ps_cell, self.gpio_intf_port))

  def modify_top(self, top):
    bd_inst = top.get_instance(self.blkdesign, '{:s}_inst'.format(self.blkdesign))

    for idx in self.spi:
      for pin, _ in self.spi_pins:
        port = self.spi_port_name(idx, pin)
        bd_inst.add_port(port, port)

    if self.gpio_width > 0:
      for pin in self.gpio_pins:
        port = '{:s}_{:s}'.format(self.gpio_intf_port, pin)
        bd_inst.add_port(port, port, width=self.gpio_width)

  def gen_children(self):
    return []

  def gen_constraints(self):
    return []

  def gen_tcl_cmds(self):
    return {}
