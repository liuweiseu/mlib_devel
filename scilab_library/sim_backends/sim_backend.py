
class SimBackend(object):
    """
    A simulation backend object generates the scripts for simlation based on different simulaters.

    There are sever methods are required at least:
    1. generate_compile_order: 
        For each VHDL/Verilog module, a specific compile order might be needed.
    2. generate_sim_script:
        generate a script for running simulation in the background.
    """
    def __init__(self, simdir, simtop):
        self.simdir = simdir
        self.simtop = simtop
        self.compile_order = {
            'vhdl': [],
            'verilog': []
        }

    def add_compile_order(self, co, type):
        """
        'co' is the compile order for a lib, which is a dict.
        It should contains two keys at least:
            * 'lib'(str): the lib name
            * 'modules'(list): the fullpath of the modules in this lib
        'type' is the file type, which should be `vhdl` or 'verilog'
        """
        if type not in self.compile_order:
            raise KeyError(f"File type '{type}' not supported.")
        self.compile_order[type].append(co)
    
    def generate_compile_order(self):
        pass

    def generate_sim_script(self):
        pass

class VivadoSimulator(SimBackend):
    """
    Use Vivado Simulator as the backend simulator.
    """
    def __init__(self, simdir, simtop):
        super.__init__(simdir, simtop)
        self.vhdl_cof = simdir + '/' + 'vhdl.prj'
        self.verilog_cof = simdir + '/' + 'vlog.prj'
        self.sim_script = simdir + '/' + 'caspersim.sh'
        self.cmdtcl = simdir + '/' + 'caspersim.tcl'

    def generate_compile_order(self):
        # generate vhdl compile order first
        with open(self.vhdl_cof, 'w') as f:
            for co in self.compile_order['vhdl']:
                f.write("vhdl {co['lib']} \\\n")
                for m in co['modules']:
                    f.write(f"     \"{m}\" \\\n")
                f.write('\n')
            f.write('\n')
            f.write('nosort')
        # generate verilog compile order
        with open(self.verilog_cof, 'w') as f:
            for co in self.compile_order['verilog']:
                f.write("vhdl {co['lib']} \\\n")
                for m in co['modules']:
                    f.write(f"     \"{m}\" \\\n")
                f.write('\n')
            f.write('\n')
            f.write('nosort')
        
    def gen_sim_scripts(self):
        # generate the simulation scripts based on the Vivado Simulator
        scripts = []
        scripts.append('#!/bin/bash -f\n\n')
        scripts.append('set -Eeuo pipefail\n\n')
        scripts.append('# set xvlog and xvhdl options\n')
        scripts.append('xvlog_opts=\"--incr --relax \"\n')
        scripts.append('xvhdl_opts=\"--incr --relax \"\n\n')
        scripts.append('# Compile \n')
        scripts.append(f"xvlog $xvlog_opts -prj {self.verilog_cof} 2>&1 | tee compile_verilog.log\n")
        scripts.append(f"xvhdl $xvhdl_opts -prj {self.vhdl_cof} 2>&1 | tee compile_vhdl.log\n\n")
        scripts.append('# Elaborate\n')
        scripts.append('xelab --incr --debug typical --relax --mt auto ')
        # get the lib names here
        libs = []
        for k in self.compile_order.keys():
            for co in self.compile_order[k]:
                if co['lib'] not in libs:
                    libs.append(co['lib'])
        # write the lib names into scripts
        for lib in libs:
            scripts.append(f'-L {lib} ')
        # These following three libs seem to be the Xilinx libs
        # They may not be necessary?
        scripts.append('-L unisims_ver -L unimacro_ver -L secureip -L xpm ')
        scripts.append(f'--snapshot {self.simtop} ')
        scripts.append(f'xil_defaultlib.{self.simtop} ')
        scripts.append('xil_defaultlib.glbl -log elaborate.log')
        scripts.append(f'xsim {self.simtop} -key {{Behavioral:sim_1:Functional:{self.simtop}}} -tclbatch {self.cmdtcl} -log simulate.log')
        