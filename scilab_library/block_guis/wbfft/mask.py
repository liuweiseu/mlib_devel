import sys
import logging
import json
import math
from argparse import ArgumentParser
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from wideband_fft_ui import Ui_MainWindow
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import make_rich_logger

WBFFT_CONFIG = {
        'use_separate':
        {
            'get': 'get_use_separate',
            'set': 'set_use_separate'
        },
        'use_fft_shift':
        {
            'get': 'get_use_fft_shift',
            'set': 'set_use_fft_shift'
        },
        'use_reorder':
        {
            'get': 'get_use_reorder',
            'set': 'set_use_reorder'
        },
        'alt_output':
        {
            'get': 'get_alt_output',
            'set': 'set_alt_output'
        },
        'wb_factor':
        {
            'get': 'get_wb_factor',
            'set': 'set_wb_factor'
        },
        'nof_points':
        {
            'get': 'get_nof_points',
            'set': 'set_nof_points'
        },
        'in_dat_w':
        {
            'get': 'get_in_dat_w',
            'set': 'set_in_dat_w'
        },
        'twiddle_dat_w':
        {
            'get': 'get_twiddle_dat_w',
            'set': 'set_twiddle_dat_w'
        }, 
        'stage_dat_w':
        {
            'get': 'get_stage_dat_w',
            'set': 'set_stage_dat_w'
        },
        'out_dat_w':
        {
            'get': 'get_out_dat_w',
            'set': 'set_out_dat_w'
        },
        'out_gain_w':
        {
            'get': 'get_out_gain_w',
            'set': 'set_out_gain_w'
        },
        'guard_enable':
        {
            'get': 'get_guard_enable',
            'set': 'set_guard_enable'
        },
        'guard_w':
        {
            'get': 'get_guard_w',
            'set': 'set_guard_w'
        },
        'use_round':
        {
            'get': 'get_use_round',
            'set': 'set_use_round'
        },
        'ovflw_behav':
        {
            'get': 'get_ovflw_behav',
            'set': 'set_ovflw_behav'
        },
        'pipe_reo_in_place':
        {
            'get': 'get_pipe_reo_in_place',
            'set': 'set_pipe_reo_in_place'
        },
        'use_dsp':
        {
            'get': 'get_use_dsp',
            'set': 'set_use_dsp'
        },
        'use_variant':
        {
            'get': 'get_use_variant',
            'set': 'set_use_variant'
        },
        'ram_primitive':
        {
            'get': 'get_ram_primitive',
            'set': 'set_ram_primitive'
        },
        'max_addr_w':
        {
            'get': 'get_max_addr_w',
            'set': 'set_max_addr_w'
        },
        'vendor':
        {
            'get': 'get_vendor',
            'set': 'set_vendor'
        }
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

class WBFFTOperations(object):
    def __init__(self, winobj, src_config='wb_fft.json', dst_config='wb_fft.json', logdir='.', debug=False):
        if debug:
            self.logger = make_rich_logger('wbfft.log', logging.DEBUG, mode='a', logdir=logdir)
        else:
            self.logger = make_rich_logger('wbfft.log', logging.ERROR, mode='a', logdir=logdir)
        self.logger.info('*************************************************')
        self.logger.info('Wideband FFT Mask started.')
        self.logger.info('*************************************************')
        self.logger.info(f'Source config file is {src_config}.')
        self.logger.info(f'Dest config file is {dst_config}.')
        self.src_config = src_config
        self.dst_config = dst_config
        self.winobj = winobj
        self.ui = winobj.ui
        if self.src_config is not None:
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
    def get_use_separate(self):
        status = self.ui.use_separate.isChecked()
        self.logger.debug(f'use_separate status is {status}')
        return self._cv(status)
    
    def set_use_separate(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set use_separate status to {status}')
        self.ui.use_separate.setChecked(status)
    
    def get_use_fft_shift(self):
        status = self.ui.use_fft_shift.isChecked()
        self.logger.debug(f'use_fft_shift status is {status}')
        return self._cv(status)

    def set_use_fft_shift(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set use_fft_shift status to {status}')
        self.ui.use_fft_shift.setChecked(status)

    def get_use_reorder(self):
        status = self.ui.use_reorder.isChecked()
        self.logger.debug(f'use_reorder status is {status}')
        return self._cv(status)
    
    def set_use_reorder(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set use_reorder status to {status}')
        self.ui.use_reorder.setChecked(status) 
    
    def get_alt_output(self):
        status = self.ui.alt_output.isChecked()
        self.logger.debug(f'alt_output status is {status}')
        return self._cv(status)
    
    def set_alt_output(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set alt_output status to {status}')
        self.ui.alt_output.setChecked(status) 

    def get_wb_factor(self):
        val = self.ui.wb_factor.value()
        self.logger.debug(f'wb_factor is {val}')
        return str(val)
    
    def set_wb_factor(self, val):
        self.logger.debug(f'Set wb_factor to {val}')
        self.ui.wb_factor.setValue(int(val))
    
    def get_nof_points(self):
        val = self.ui.nof_points.value()
        self.logger.debug(f'nof_points is {val}')
        return str(2**val)
    
    def set_nof_points(self, val):
        self.logger.debug(f'Set nof_points to {val}')
        self.ui.nof_points.setValue(int(math.log2(val)))
    
    def get_in_dat_w(self):
        val = self.ui.in_dat_w.value()
        self.logger.debug(f'in_dat_w is {val}')
        return str(val)
    
    def set_in_dat_w(self, val):
        self.logger.debug(f'Set in_dat_w to {val}')
        self.ui.in_dat_w.setValue(int(val))

    def get_twiddle_dat_w(self):
        val = self.ui.twiddle_dat_w.value()
        self.logger.debug(f'twiddle_dat_w is {val}')
        return str(val)
    
    def set_twiddle_dat_w(self, val):
        self.logger.debug(f'Set twiddle_dat_w to {val}')
        self.ui.twiddle_dat_w.setValue(int(val))
    
    def get_stage_dat_w(self):
        val = self.ui.stage_dat_w.value()
        self.logger.debug(f'stage_dat_w is {val}')
        return str(val)
    
    def set_stage_dat_w(self, val):
        self.logger.debug(f'Set stage_dat_w to {val}')
        self.ui.stage_dat_w.setValue(int(val))
    
    def get_out_dat_w(self):
        val = self.ui.out_dat_w.value()
        self.logger.debug(f'out_dat_w is {val}')
        return str(val)
    
    def set_out_dat_w(self, val):
        self.logger.debug(f'Set out_dat_w to {val}')
        self.ui.out_dat_w.setValue(int(val))

    def get_out_gain_w(self):
        val = self.ui.out_gain_w.value()
        self.logger.debug(f'out_gain_w is {val}')
        return str(val)
    
    def set_out_gain_w(self, val):
        self.logger.debug(f'Set out_gain_w to {val}')
        self.ui.out_gain_w.setValue(int(val))
    
    def get_guard_enable(self):
        status = self.ui.guard_enable.isChecked()
        self.logger.debug(f'guard_enable status is {status}')
        return self._cv(status)
    
    def set_guard_enable(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set guard_enable status to {status}')
        self.ui.guard_enable.setChecked(status) 
    
    def get_use_round(self):
        index = self.ui.use_round.currentIndex()
        text = self.ui.use_round.currentText()
        self.logger.debug(f'use_round is {text}({index})')
        return str(index)
    
    def set_use_round(self, index):
        text = ['Truncate', 'Round Even', 'Round Infinite']
        self.logger.debug(f"Set use_round to {text[index]}({index})")
        self.ui.use_round.setCurrentIndex(index)
    
    def get_ovflw_behav(self):
        index = self.ui.ovflw_behav.currentIndex()
        text = self.ui.ovflw_behav.currentText()
        self.logger.debug(f'ovflw_behav is {text}({index})')
        return text
    
    def set_ovflw_behav(self, text):
        self.logger.debug(f"Set ovflw_behav to {text})")
        self.ui.ovflw_behav.setCurrentText(text)

    def get_pipe_reo_in_place(self):
        status = self.ui.pipe_reo_in_place.isChecked()
        self.logger.debug('pipe_reo_in_place status is {status}')
        return self._cv(status)

    def set_pipe_reo_in_place(self, status):
        status = self._cv(status)
        self.logger.debug(f'Set pipe_reo_in_place stauts to {status}')
        self.ui.pipe_reo_in_place.setChecked(status)
    
    def get_use_dsp(self):
        index = self.ui.use_dsp.currentIndex()
        text = self.ui.use_dsp.currentText()
        self.logger.debug(f'use_dsp is {text}({index})')
        return text
    
    def set_use_dsp(self, text):
        self.logger.debug(f"Set use_dsp to {text})")
        self.ui.use_dsp.setCurrentText(text)

    def get_use_variant(self):
        index = self.ui.use_variant.currentIndex()
        text = self.ui.use_variant.currentText()
        self.logger.debug(f'use_variant is {text}({index})')
        return text
    
    def set_use_variant(self, text):
        self.logger.debug(f"Set use_variant to {text})")
        self.ui.use_variant.setCurrentText(text)
    
    def get_ram_primitive(self):
        index = self.ui.ram_primitive.currentIndex()
        text = self.ui.ram_primitive.currentText()
        self.logger.debug(f'ram_primitive is {text}({index})')
        return text
    
    def set_ram_primitive(self, text):
        self.logger.debug(f"Set ram_primitive to {text})")
        self.ui.ram_primitive.setCurrentText(text)

    def get_max_addr_w(self):
        val = self.ui.max_addr_w.value()
        self.logger.debug(f'max_addr_w is {val}')
        return str(val)
    
    def set_max_addr_w(self, val):
        self.logger.debug(f'Set max_addr_w to {val}')
        self.ui.max_addr_w.setValue(int(val))
    
    def get_vendor(self):
        index = self.ui.vendor.currentIndex()
        text = self.ui.vendor.currentText()
        self.logger.debug(f'vendor is {text}({index})')
        return str(index)
    
    def set_vendor(self, index):
        text = ['Xilinx', 'UniBoard']
        self.logger.debug(f"Set vendor to {text[index]}({index})")
        self.ui.vendor.setCurrentIndex(index)

    def get_guard_w(self):
        val = self.ui.guard_w.value()
        self.logger.debug(f'guard_w is {val}')
        return str(val)
    
    def set_guard_w(self, val):
        self.logger.debug(f'Set guard_w to {val}')
        self.ui.guard_w.setValue(int(val))
    
    def set_guard_w_status(self, status):
        self.ui.guard_w.setEnabled(status)

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

    def GuardEnable_Checked(self):
        self.logger.info('---------------------------------------------')
        self.logger.info('Guard Enable status changed.')
        self.logger.info('---------------------------------------------')
        status = self.get_guard_enable()
        if self._cv(status):
            self.set_guard_w_status(True)
        else:
            self.set_guard_w_status(False)

    # *******************************************************************
    # Setup Signal functions
    # *******************************************************************
    def setup_signal_functions(self):
        self.ui.button_ok.clicked.connect(self.ButtonOK_Clicked)
        self.ui.button_cancel.clicked.connect(self.ButtonCancel_Clicked)
        self.ui.button_apply.clicked.connect(self.ButtonApply_Clicked)
        self.ui.guard_enable.clicked.connect(self.GuardEnable_Checked)

    # *******************************************************************
    # load/collect config functions
    # *******************************************************************
    def load_config(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Loading default config from {self.src_config}...')
        self.logger.info('-------------------------------------------------')
        with open(self.src_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        parameters = config['parameters']
        for k,v in parameters.items():
            if k in WBFFT_CONFIG:
                setfunc = WBFFT_CONFIG[k]['set']
                try:
                    v = int(v)
                except:
                    pass
                getattr(self, setfunc)(v)

    def collect_config(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Writing config data to {self.dst_config}...')
        self.logger.info('-------------------------------------------------')
        # try to open the config file if it exists
        try:
            with open(self.dst_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
            config['parameters'] = {}
            config['parameters']['name'] = ''
            config['parameters']['fullpath'] = ''
            config['parameters']['tag'] = 'dsp:wbfft'
        for k,v in WBFFT_CONFIG.items():
            key = k
            getfunc = v['get']
            config['parameters'][f'{key}'] = str(getattr(self, getfunc)())
        with open(self.dst_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = ArgumentParser(description="Usage for RFDC Mask.")
    parser.add_argument('-s','--src', type=str, dest='src', default=None, help='Source config file.')
    parser.add_argument('-d','--dst', type=str, dest='dst', default='wbfft.json',help='Dest config file.')
    parser.add_argument('-l', '--log', type=str, dest='log', default='.', help='The directory for log files.')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true', default=False, help='Turn on verbose.')
    opts = parser.parse_args()

    app = QApplication(sys.argv)
    script_path = os.path.realpath(__file__)
    curdir = os.path.dirname(script_path)
    app.setWindowIcon(QIcon(f"{curdir}/icon/casper_icon.png"))
    win = MainWindow()
    op = WBFFTOperations(win, opts.src, opts.dst, opts.log, opts.debug)
    win.show()
    sys.exit(app.exec())