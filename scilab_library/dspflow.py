import sys, os
sys.path.append('../jasper_library')

import logging
import yaml
from toolflow import Toolflow
import dsp_blocks.dsp_block as dsp_block

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
        self.dsp_modules = None
        self.constraints = None
        self.sources = []
        self.ips = []
        self.tcl_sources = []
        self.const_files = []
    
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