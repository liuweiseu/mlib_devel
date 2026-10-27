import sys
from .dsp_block import DSPBlock
from verilog import VerilogModule

class delay(DSPBlock):
    # Xilinx Delay block on casper_dsp's BasicModules/delay.v (the same RTL
    # module "delay" that many casper_dsp modules instantiate internally, so
    # a design that mixes them compiles one single definition of it).
    SRC = 'casper_dsp/rtl/BasicModules/delay.v'

    def initialize(self):
        self.add_source(self.SRC)

    @staticmethod
    def _enable_val(status):
        # checkbox status is saved as 'on'/'off' (see mask.py's _convert_status);
        # val_format_conv turns it into True/False
        return 1 if str(status).strip().lower() in ('on', '1', 'true') else 0

    def _n_bits(self):
        return int(float(self.n_bits))

    def modify_top(self,top):
        # let's populate the parent ports first
        self._populate_parent_ports(top)
        # create a verilog module
        module = 'delay'
        inst = top.get_instance(entity=module, name=self.fullname)
        # add parameters -- one per delay.v parameter, in declaration order
        inst.add_parameter("LATENCY", "%d" % int(float(self.latency)))
        inst.add_parameter("BITWIDTH", "%d" % self._n_bits())
        inst.add_parameter("USE_RST", "%d" % self._enable_val(self.rst))
        inst.add_parameter("USE_ENABLE", "%d" % self._enable_val(self.en))
        # add ports -- names match delay.v's port list; the optional ones
        # follow delay.sci's port list (delay_in_ports). rst / en have default
        # values (0 / 1) in delay.v, so they are left unconnected when absent.
        inst.add_port('clk', 'user_clk', dir='in')
        for name, width in self.in_ports():
            inst.add_port(name, self.fullname + '_' + name, parent_port=False, width=width, dir='in')
        inst.add_port('dout', self.fullname + '_dout', parent_port=False, width=self._n_bits(), dir='out')

    def in_ports(self):
        """(name, width) of the input ports, in Xcos port order: din, then
        rst and en when their option is on (Simulink order d, rst, en)."""
        ports = [('din', self._n_bits())]
        if self._enable_val(self.rst):
            ports += [('rst', 1)]
        if self._enable_val(self.en):
            ports += [('en', 1)]
        return ports

    def generate_compile_order(self):
        fullpath = self.hdl_root + '/'
        co = {
            'lib': 'xil_defaultlib',
            'modules': [
                fullpath + self.SRC
            ],
            'fullpath': True
        }
        self.compile_order['verilog'].append(co)
