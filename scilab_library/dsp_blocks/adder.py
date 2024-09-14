import sys
from dsp_block import DSPBlock

class Adder(DSPBlock):
    def __init__(self):
        print('init adder')

    #def initialize(self):
    #    print('hello')

if __name__ == '__main__':
    adder = Adder()
    adder.initialize()