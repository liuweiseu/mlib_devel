#! /usr/bin/env python

import os
import sys
sys.path.append('../jasper_library')
import logging
from argparse import ArgumentParser
import toolflow

if __name__ == '__main__':
    parser = ArgumentParser(prog=os.path.basename(__file__))
                            
    parser.add_argument("-c", "--builddir", dest="builddir", type=str,
                default='',
                help="build directory. Default: Use directory with same "
                    "name as model")
    parser.add_argument("--jobs", dest="jobs", type=int, default=4,
                    help="Number of cores to run compiles with. Default=4")
    parser.add_argument("--be", dest="be", type=str, default='vivado',
                    help="Backend to use. Default: vivado")
    
    opts = parser.parse_args()

    # get build directory
    # use user defined directory else use a directory with same name as model
    builddir = opts.builddir or opts.model.split('.')[0]

    # create the build directory, and log file
    os.system('mkdir -p %s' % builddir)
    logger = logging.getLogger('jasper_dsp')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('%s/jasper-dsp.log' % builddir, mode='w')
    handler.setLevel(logging.DEBUG)
    logformat = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
    handler.setFormatter(logformat)
    logger.addHandler(handler)
    logger.info('Starting generating DSP IP')
