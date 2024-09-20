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
        inst.add_port('in0', self.fullname+'_in0', parent_port = True, width=32, dir='in')
        inst.add_port('in1', self.fullname+'_in1', parent_port = True, width=32, dir='in')
        inst.add_port('out', self.fullname+'_out0', parent_port = True, width=32, dir='out')

        