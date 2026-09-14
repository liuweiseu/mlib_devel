import sys
import logging
import json
from argparse import ArgumentParser
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from sw_reg_ui import Ui_MainWindow
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import make_rich_logger, gen_bconfig

# Mapping between the JSON parameter keys (as produced by the legacy
# xps_library swreg mask - see software_register_init.m/swreg_init.m/
# swreg_maskcheck.m) and the get/set methods used to synchronize them
# with the Qt widgets defined in sw_reg_ui.py.
SWREG_CONFIG = {
    'io_dir':
    {
        'get': 'get_io_dir',
        'set': 'set_io_dir'
    },
    'mode':
    {
        'get': 'get_mode',
        'set': 'set_mode'
    },
    'names':
    {
        'get': 'get_names',
        'set': 'set_names'
    },
    'bitwidths':
    {
        'get': 'get_bitwidths',
        'set': 'set_bitwidths'
    },
    'bin_pts':
    {
        'get': 'get_bin_pts',
        'set': 'set_bin_pts'
    },
    'arith_types':
    {
        'get': 'get_arith_types',
        'set': 'set_arith_types'
    },
    'io_delay':
    {
        'get': 'get_io_delay',
        'set': 'set_io_delay'
    },
    'sample_period':
    {
        'get': 'get_sample_period',
        'set': 'set_sample_period'
    },
    'sim_port':
    {
        'get': 'get_sim_port',
        'set': 'set_sim_port'
    },
    'show_format':
    {
        'get': 'get_show_format',
        'set': 'set_show_format'
    }
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


class SWREGOperations(object):
    def __init__(self, winobj, template_config='sw_reg.json', target_config='sw_reg.json', logdir='.', debug=False):
        if debug:
            self.logger = make_rich_logger('sw_reg.log', logging.DEBUG, mode='a', logdir=logdir)
        else:
            self.logger = make_rich_logger('sw_reg.log', logging.ERROR, mode='a', logdir=logdir)
        self.logger.info('*************************************************')
        self.logger.info('Software Register Mask started.')
        self.logger.info('*************************************************')
        self.logger.info(f'Source config file is {template_config}.')
        self.logger.info(f'Dest config file is {target_config}.')
        self.template_config = template_config
        self.target_config = target_config
        self.winobj = winobj
        self.ui = winobj.ui
        self.load_config()
        self.setup_signal_functions()

    def _cv(self, v):
        if v == True:
            return 1
        elif v == False:
            return 0
        elif v == 1:
            return True
        elif v == 0:
            return False
        else:
            self.logger.error(f' Value({v}) not supported')

    # *******************************************************************
    # Low-level APIs
    # *******************************************************************
    def get_io_dir(self):
        text = self.ui.io_dir.currentText()
        self.logger.debug(f'io_dir is {text}')
        return text

    def set_io_dir(self, text):
        self.logger.debug(f'Set io_dir to {text}')
        self.ui.io_dir.setCurrentText(str(text))

    def get_mode(self):
        text = self.ui.mode.currentText()
        self.logger.debug(f'mode is {text}')
        return text

    def set_mode(self, text):
        self.logger.debug(f'Set mode to {text}')
        self.ui.mode.setCurrentText(str(text))

    def get_names(self):
        val = self.ui.names.text()
        self.logger.debug(f'names is {val}')
        return val

    def set_names(self, val):
        self.logger.debug(f'Set names to {val}')
        self.ui.names.setText(str(val))

    def get_bitwidths(self):
        val = self.ui.bitwidths.text()
        self.logger.debug(f'bitwidths is {val}')
        return val

    def set_bitwidths(self, val):
        self.logger.debug(f'Set bitwidths to {val}')
        self.ui.bitwidths.setText(str(val))

    def get_bin_pts(self):
        val = self.ui.bin_pts.text()
        self.logger.debug(f'bin_pts is {val}')
        return val

    def set_bin_pts(self, val):
        self.logger.debug(f'Set bin_pts to {val}')
        self.ui.bin_pts.setText(str(val))

    def get_arith_types(self):
        val = self.ui.arith_types.text()
        self.logger.debug(f'arith_types is {val}')
        return val

    def set_arith_types(self, val):
        self.logger.debug(f'Set arith_types to {val}')
        self.ui.arith_types.setText(str(val))

    def get_io_delay(self):
        val = self.ui.io_delay.value()
        self.logger.debug(f'io_delay is {val}')
        return str(val)

    def set_io_delay(self, val):
        self.logger.debug(f'Set io_delay to {val}')
        self.ui.io_delay.setValue(int(val))

    def get_sample_period(self):
        val = self.ui.sample_period.value()
        self.logger.debug(f'sample_period is {val}')
        return str(val)

    def set_sample_period(self, val):
        self.logger.debug(f'Set sample_period to {val}')
        self.ui.sample_period.setValue(int(val))

    def get_sim_port(self):
        status = self.ui.sim_port.isChecked()
        self.logger.debug(f'sim_port status is {status}')
        return self._cv(status)

    def set_sim_port(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set sim_port status to {status}')
        self.ui.sim_port.setChecked(status)

    def get_show_format(self):
        status = self.ui.show_format.isChecked()
        self.logger.debug(f'show_format status is {status}')
        return self._cv(status)

    def set_show_format(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set show_format status to {status}')
        self.ui.show_format.setChecked(status)

    def set_bitfields_status(self, status):
        """
        Enable/disable the bitwidths/bin_pts/arith_types fields.
        These only make sense in 'fields of ...' modes, following the same
        pattern as swreg_cb.m's dynamic MaskEnables/MaskPrompts behaviour.
        """
        self.ui.bitwidths.setEnabled(status)
        self.ui.bin_pts.setEnabled(status)
        self.ui.arith_types.setEnabled(status)

    def set_sample_period_status(self, status):
        self.ui.sample_period.setEnabled(status)

    # *******************************************************************
    # Signal functions
    # *******************************************************************
    def ButtonOK_Clicked(self):
        self.logger.info('---------------------------------------------')
        self.logger.info('Button OK clicked, collecting info...')
        self.logger.info('---------------------------------------------')
        self.collect_config()
        self.winobj.close()

    def ButtonCancel_Clicked(self):
        self.logger.info('---------------------------------------------')
        self.logger.info('Button Cancel clicked...')
        self.logger.info('---------------------------------------------')
        self.winobj.close()

    def ButtonApply_Clicked(self):
        self.logger.info('---------------------------------------------')
        self.logger.info('Button Apply clicked, collecting info...')
        self.logger.info('---------------------------------------------')
        self.collect_config()

    def Mode_Changed(self):
        self.logger.info('---------------------------------------------')
        self.logger.info('Mode changed.')
        self.logger.info('---------------------------------------------')
        mode = self.get_mode()
        if mode == 'one value':
            self.set_bitfields_status(False)
        else:
            self.set_bitfields_status(True)

    def IODir_Changed(self):
        self.logger.info('---------------------------------------------')
        self.logger.info('IO direction changed.')
        self.logger.info('---------------------------------------------')
        io_dir = self.get_io_dir()
        if io_dir == 'From Processor':
            self.set_sample_period_status(True)
        else:
            self.set_sample_period_status(False)

    # *******************************************************************
    # Setup Signal functions
    # *******************************************************************
    def setup_signal_functions(self):
        self.ui.button_ok.clicked.connect(self.ButtonOK_Clicked)
        self.ui.button_cancel.clicked.connect(self.ButtonCancel_Clicked)
        self.ui.button_apply.clicked.connect(self.ButtonApply_Clicked)
        self.ui.mode.currentIndexChanged.connect(self.Mode_Changed)
        self.ui.io_dir.currentIndexChanged.connect(self.IODir_Changed)

    # *******************************************************************
    # load/collect config functions
    # *******************************************************************
    def load_config(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Loading config from {self.target_config}...')
        self.logger.info('-------------------------------------------------')
        with open(self.target_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        parameters = config['parameters']
        for k, v in parameters.items():
            if k in SWREG_CONFIG:
                setfunc = SWREG_CONFIG[k]['set']
                try:
                    v = int(v)
                except:
                    pass
                getattr(self, setfunc)(v)
        # apply the dynamic enable/disable rules once the config is loaded
        self.Mode_Changed()
        self.IODir_Changed()

    def collect_config(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Writing config data to {self.target_config}...')
        self.logger.info('-------------------------------------------------')
        # try to open the config file if it exists
        try:
            with open(self.target_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
            config['parameters'] = {}
            config['parameters']['name'] = ''
            config['parameters']['fullpath'] = ''
            config['parameters']['tag'] = 'xps:sw_reg'
        for k, v in SWREG_CONFIG.items():
            key = k
            getfunc = v['get']
            config['parameters'][f'{key}'] = str(getattr(self, getfunc)())
        with open(self.target_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser(description="Usage for Software Register Mask.")
    parser.add_argument('--template', type=str, dest='template', default=None, help='template config file.')
    parser.add_argument('--target', type=str, dest='target', default='sw_reg.json', help='target config file.')
    parser.add_argument('-l', '--log', type=str, dest='log', default='.', help='The directory for log files.')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true', default=False, help='Turn on verbose.')
    opts = parser.parse_args()
    # generate the bconfig file
    gen_bconfig(opts.template, opts.target)

    app = QApplication(sys.argv)
    script_path = os.path.realpath(__file__)
    curdir = os.path.dirname(script_path)
    app.setWindowIcon(QIcon(f"{curdir}/icon/casper_icon.png"))
    win = MainWindow()
    op = SWREGOperations(win, opts.template, opts.target, opts.log, opts.debug)
    win.show()
    sys.exit(app.exec())
