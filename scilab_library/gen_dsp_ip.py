#! /usr/bin/env python

import os
import sys
sys.path.append('../jasper_library')
sys.path.append('../jasper_library/yellow_blocks')

import logging
from argparse import ArgumentParser
import dspflow

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

    tf = dspflow.DSPflow(builddir, opts.jobs)
    tf.gen_dsp_objs()
    tf.build_top()
    tf.generate_hdl()
    tf.dump_castro(tf.compile_dir+'/castro.yml')
    # use Non-project mode to genenrate the vivado project
    # TODO: Do we need project mode to generate this project?
    if opts.be == 'vivado':
        platform = tf.plat
        platform.project_mode = True
        backend = dspflow.VivadoDSPBackend(plat=platform,
                                                compile_dir=tf.compile_dir,
                                                periph_objs=tf.periph_objs)
        backend.import_from_castro(backend.compile_dir + '/castro.yml')
        # set a new project name, so that it's different from the original project(myproj)
        backend.project_name = 'dspproj'
        backend.initialize()
        backend.compile(cores=opts.cores, plat=platform)
    else:
        # TODO: Add support for other backends
        pass
