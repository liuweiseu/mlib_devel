import sys, os
sys.path.append('../jasper_library')

import logging
import yaml
import pickle
from toolflow import Toolflow
import dsp_blocks.dsp_block as dsp_block
import verilog

class DSPflow(Toolflow):
    """
    This class is used for generating a vivado project for DSP blocks.
    An IP core will be created from this project, which only contains all of the dsp blocks.
    """
    def __init__(self, compile_dir='/tmp', jobs = 8):
        self.jobs = jobs
        # setup the logger
        self.logger = logging.getLogger('jasper.dspflow')
        self.logger.info('Starting DSPflow!')
        # set the compile directory
        self.compile_dir = compile_dir.rstrip('/')
        # set the periph file
        self.dsp_file = self.compile_dir + '/jasper.dsp'
        # set the vars
        self.cores = None
        self.topfile = None
        self.top = None
        self.dsp_objs = None
        # In dspflow, we don't have peripherals.
        # The reason we have this attribute is that the yellow_block class uses it.
        self.periph_objs = None
        self.dsp_modules = None
        self.constraints = None
        self.sources = []
        self.ips = []
        self.tcl_sources = []
        self.const_files = []
        # by default, we don't have user modules.
        self.user_modules = {}
        
    
    def _parse_dsp_file(self):
        """
        Open the peripherals file and parse it's
        contents using the pyaml package.
        Write the resulting yellow_blocks
        and user_modules dictionaries to
        attributes
        """
        self.logger.info('Parsing DSP file.')
        if not os.path.exists(self.dsp_file):
            self.logger.error('dsp file doesn\'t exist!')
            raise Exception('dsp file doesn\'t exist!')
        with open(self.dsp_file, 'r') as fh:
            yaml_dict = yaml.load(fh, Loader=yaml.Loader)
        self.dsp_modules = yaml_dict['dsp_blocks']

    def gen_dsp_objs(self):
        """
        Generate a list of dsp blocks from the current dsp file.

        Internally, calls:

        * ``_parse_dsp_file``: parses .dsp file
        * ``_extract_plat_info``: instantiates platform instance

        Then calls each yellow block's constructor.
        Runs a system-wide drc before returning.
        """
        self.logger.info('Starting to generate DSP Blocks.')
        self._parse_dsp_file()
        # as other methods use the peripherals attribute in yellow_block class,
        # we need to set it to dsp_modules
        self.peripherals = self.dsp_modules
        self._extract_plat_info()
        self.dsp_objs = []
        for pk in list(sorted(self.dsp_modules.keys())):
            # we have a special xps block here, whicn contains the platform info,
            # so we have to skip it.
            if self.dsp_modules[pk]['tag'].startswith('xps:'):
                continue
            self.logger.debug('Generating DSP Block: %s' % pk)
            self.dsp_objs.append(dsp_block.DSPBlock.make_block(
                self.dsp_modules[pk], self.plat))
        self._expand_children(self.dsp_objs)
        # some methods in yellow_block class use the peripherals attribute,
        # so we have to set it to dsp_modules
        self.periph_objs = self.dsp_objs
    
    def build_top(self):
        """
        This method is almost the same as the one in the Toolflow class.
        The difference is the two "try...except..." are removed.
        Not sure why the "try...except..." are used in the Toolflow class.
        """
        self.topfile = self.compile_dir+'/top.v'
        # delete top.v file if it exists, otherwise synthesis will fail
        if os.path.exists(self.topfile):
            os.remove(self.topfile)
        # os.system('cp %s %s'%(basetopfile, self.topfile))
        self.sources.append(self.topfile)
        for source in self.plat.sources:
            self.sources.append(os.getenv('HDL_ROOT')+'/'+source)
        for source in self.plat.consts:
            self.const_files.append(os.getenv('HDL_ROOT') + '/%s/%s' % (
                self.plat.name, source))
        if os.path.exists(self.topfile):
            self.top = verilog.VerilogModule(name='top', topfile=self.topfile)
        else:
            self.top = verilog.VerilogModule(name='top')
    
    def _instantiate_periphs(self):
        """
        Calls each dsp block's modify_top method against the class'
        top VerilogModule instance.
        We don't have axi modules in the dsp blocks, so the axi related code is removed here.
        """
        self.logger.info('top: %s' % self.topfile)
        for obj in self.periph_objs:
            self.logger.debug('modifying top for obj %s' % obj.name)
            # self.top.set_cur_blk(obj.fullname)
            if '/' in obj.fullpath:
                obj.fullpath = obj.fullpath.partition('/')[2]
            self.top.set_cur_blk('%s: %s'%(obj.tag.split(':')[1], obj.fullpath))
            obj.modify_top(self.top)
            self.sources += obj.sources
            self.ips += obj.ips
    
    def regenerate_top(self):
        """
        Generate the verilog for the modified top
        module. This involves computing the wishbone
        interconnect / addressing and generating new
        code for yellow block instances.
        """
        # Write top module file
        self.top.gen_module_file(filename=self.compile_dir+'/top.v')
        # Write any submodule files required for the compile. This is probably
        # only the hierarchical WB arbiter, or nothing at all
        for key, val in self.top.generated_sub_modules.items():
            self.logger.info("Writing sub module file %s.v" % key)
            with open(self.compile_dir+'/%s.v'%key, 'w') as fh:
                fh.write(val)
                self.sources.append(fh.name)
        self.logger.info("Dumping pickle of top-level Verilog module")
        pickle.dump(self.top, open('%s/top.pickle' % self.compile_dir,'wb'))
