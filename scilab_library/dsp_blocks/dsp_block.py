import sys
# add the jasper_library to the path
sys.path.append('../../jasper_library')
sys.path.append('../../jasper_library/yellow_blocks')

import collections
from yellow_block import YellowBlock

class DSPBlock(YellowBlock):
    # The DSPBlock class is a subclass of the YellowBlock class
    # All of the dsp blocks will override:
    # 1. the initialize method
    # 2. the modify method 
    # 3. make_block method, as the tag for dsp blocks is different
    def initialize(self):
        print('in DSPBlock initialize')
    
    def modify(self, design, top_module):
        print('in DSPBlock modify')
    
    @staticmethod
    def make_block(blk, platform, hdl_root=None):
        if blk['tag'].startswith('xps:'):
            # This seems a little dubious
            # Import the yellow block from the same package
            # that this YellowBlock class lives
            clsfile = __import__(__package__+'.'+blk['tag'][4:])
            cls = clsfile.__getattribute__(blk['tag'][4:])
            cls = cls.__getattribute__(blk['tag'][4:]) # don't understand
            # If the class has a factory method, call that. This should return some
            # (possibly platform dependent) yellow block instance
            # Else just return an instance of the class.
            if isinstance(getattr(cls, 'factory', None), collections.Callable):
                return cls.factory(blk, platform, hdl_root=hdl_root)
            else:
                return cls(blk,platform,hdl_root=hdl_root)
        else:
            # Don't do anything for non-xps blocks.
            pass