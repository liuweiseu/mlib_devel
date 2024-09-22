import os, json
from glob import glob
mlib_devel_path = os.getenv('MLIB_DEVEL_PATH')

import sys
# add the jasper_library to the path
sys.path.append('jasper_library')
sys.path.append('jasper_library/yellow_blocks')
print(os.getcwd())
import collections
from yellow_block import YellowBlock

class DSPBlock(YellowBlock):
    # The DSPBlock class is a subclass of the YellowBlock class
    # All of the dsp blocks will override:
    # 1. __init__ method
    # 2. the initialize method
    # 3. the modify method 
    # 4. make_block method, as the tag for dsp blocks is different
    def __init__(self, blk, platform, hdl_root=None, link_info_file = mlib_devel_path+'/jasper.json'):
        # The __init__ method of the DSPBlock class takes in the following arguments:
        # 1. self
        # 2. blk
        # 3. platform
        # 4. hdl_root
        # 5. link_info_file
        # The __init__ method of the DSPBlock class initializes
        super(DSPBlock, self).__init__(blk, platform, hdl_root=hdl_root)
        self.link_info_file = link_info_file
        # populate the parent ports
        self._get_parent_ports_info()

    def initialize(self):
        pass
    
    def modify(self, design, top_module):
        pass
    
    @staticmethod
    def make_block(blk, platform, hdl_root=None):
        if blk['tag'].startswith('dsp:'):
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
    
    def _get_parent_ports_info(self):
        # we need to get the link info here
        with open(self.link_info_file) as f:
            blkinfo = json.load(f)
            self.link_info = blkinfo['link_info']
        self.parent_ports = {}
        self.parent_ports['in'] = []
        self.parent_ports['out'] = []
        for link in self.link_info:
            if link['dst_blk_name'] == self.unique_name and link['link_type'] == 'xps_dsp':
                    self.parent_ports['in'].append(link)
            if link['src_blk_name'] == self.unique_name and link['link_type'] == 'dsp_xps':
                    self.parent_ports['out'].append(link)
    
    def _populate_parent_ports(self, top):
        for link in self.parent_ports['in']:
             top.add_port(link['src_port_name'], width=link['src_port_width'], dir='in')
             top.assign_signal(link['dst_port_name'], link['src_port_name']) 
        for link in self.parent_ports['out']:
            top.add_port(link['dst_port_name'], width=link['dst_port_width'], dir='out')
            top.assign_signal(link['src_port_name'], link['dst_port_name'])
    