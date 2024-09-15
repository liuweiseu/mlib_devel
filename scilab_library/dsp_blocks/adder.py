import sys
from .dsp_block import DSPBlock
from verilog import VerilogModule

class adder(DSPBlock):
    def initialize(self):
        self.add_source('adder/*')

    def modify_top(self,top):
        # create a verilog module
        module = 'adder'
        inst = top.get_instance(entity=module, name=self.fullname)
        # TODO: add parameters
        # add ports
        inst.add_port('clk', 'clk', parent_port=True, dir='in')
        inst.add_port('a', self.fullname+'_a', parent_port = True, width=32, dir='in')
        inst.add_port('b', self.fullname+'_b', parent_port = True, width=32, dir='in')
        inst.add_port('sum', self.fullname+'_sum', parent_port = True, width=32, dir='out')

        