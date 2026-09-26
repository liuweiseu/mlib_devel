import sys
from .dsp_block import DSPBlock
from verilog import VerilogModule

class counter(DSPBlock):
    # GUI values ("Free Running"/"Count Limited", "Up"/"Down"/"Up/Down") map
    # onto counter.sv's COUNTER_TYPE/COUNT_DIR integer encodings.
    COUNTER_TYPE_MAP = {'Free Running': 0, 'Count Limited': 1}
    COUNT_DIR_MAP = {'Up': 0, 'Down': 1, 'Up/Down': 2}

    def initialize(self):
        self.add_source('casper_dsp/rtl/BasicModules/counter.sv')

    @staticmethod
    def _enable_val(status):
        # checkbox status is saved as 'on'/'off' (see mask.py's _convert_status)
        return 1 if str(status).strip().lower() in ('on', '1', 'true') else 0

    def modify_top(self,top):
        # let's populate the parent ports first
        self._populate_parent_ports(top)
        # create a verilog module
        module = 'counter'
        inst = top.get_instance(entity=module, name=self.fullname)
        # add parameters -- one per counter.sv parameter, in the same order
        # they're declared there
        inst.add_parameter("COUNTER_TYPE", "32'd%d" % self.COUNTER_TYPE_MAP[self.counter_type])
        inst.add_parameter("NBITS", "32'd%d" % int(self.n_bits))
        inst.add_parameter("COUNT_TO_VAL", "32'd%d" % int(self.count_to_val))
        inst.add_parameter("COUNT_DIR", "32'd%d" % self.COUNT_DIR_MAP[self.count_dir])
        inst.add_parameter("INIT_VAL", "32'd%d" % int(self.init_val))
        inst.add_parameter("STEP", "32'd%d" % int(self.step))
        inst.add_parameter("BIN_P", "32'd%d" % int(self.bin_pt))
        inst.add_parameter("ENABLE_LOAD", "32'd%d" % self._enable_val(self.enable_load))
        inst.add_parameter("ENABLE_SYNC_RST", "32'd%d" % self._enable_val(self.enable_sync_rst))
        inst.add_parameter("ENABLE_ENABLE", "32'd%d" % self._enable_val(self.enable_enable))
        # add ports -- names match counter.sv's port list exactly
        # we need to check if the port is in parent_ports
        inst.add_port('clk', 'user_clk', dir='in')
        inst.add_port('rst', self.fullname+'_rst', parent_port=False, width=1, dir='in')
        inst.add_port('enable', self.fullname+'_enable', parent_port=False, width=1, dir='in')
        inst.add_port('dout', self.fullname+'_dout', parent_port=False, width=int(self.n_bits), dir='out')

    def generate_compile_order(self):
        fullpath = self.hdl_root + '/'
        co = {
            'lib': 'xil_defaultlib',
            'modules': [
                fullpath + 'casper_dsp/rtl/BasicModules/counter.sv'
            ],
            'fullpath': True
        }
        self.compile_order['verilog'].append(co)
