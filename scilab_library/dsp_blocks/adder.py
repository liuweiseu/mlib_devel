import sys
from .dsp_block import DSPBlock
from verilog import VerilogModule

class adder(DSPBlock):
    def initialize(self):
        self.add_source('adder/*')

    def modify_top(self,top):
        # create a verilog module
        module = 'adder'
        inst = VerilogModule(entity=module, name=self.fullname)
        # TODO: add parameters
        # add ports
        inst.add_port('clk', 'clk')
        inst.add_port('a', self.fullname+'_a')
        inst.add_port('b', self.fullname+'_b')
        inst.add_port('sum', self.fullname+'_sum')
        # Add the adder module to the top
        top.add_signal(self.fullname+'_a', 32)
        top.add_signal(self.fullname+'_b', 32)
        top.add_signal(self.fullname+'_sum', 32)
        