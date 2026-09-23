import sys
import logging
import json
from argparse import ArgumentParser
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtGui import QIcon
import os
from munge_ui import Ui_MainWindow

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import make_rich_logger, gen_bconfig

# Mapping between the JSON parameter keys and the get/set methods used to
# synchronize them with the Qt widgets defined in munge_ui.py.
# The keys must match scilab_blocks/casper_dsp/munge.json, since the
# Scilab side (update_exprs) only reads back the keys listed in that template.
MUNGE_CONFIG = {
    'total_bits':
    {
        'get': 'get_total_bits',
        'set': 'set_total_bits'
    },
    'divisions':
    {
        'get': 'get_divisions',
        'set': 'set_divisions'
    },
    'size_bits':
    {
        'get': 'get_size_bits',
        'set': 'set_size_bits'
    },
    'packing_order':
    {
        'get': 'get_packing_order',
        'set': 'set_packing_order'
    },
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


class MungeOperations(object):
    def __init__(self, winobj, template_config='munge.json', target_config='munge.json', logdir='.', debug=False):
        if debug:
            self.logger = make_rich_logger('munge.log', logging.DEBUG, mode='a', logdir=logdir)
        else:
            self.logger = make_rich_logger('munge.log', logging.ERROR, mode='a', logdir=logdir)
        self.logger.info('*************************************************')
        self.logger.info('Munge Mask started.')
        self.logger.info('*************************************************')
        self.logger.info(f'Source config file is {template_config}.')
        self.logger.info(f'Dest config file is {target_config}.')
        self.template_config = template_config
        self.target_config = target_config
        self.winobj = winobj
        self.ui = winobj.ui
        self.load_config()
        self.setup_signal_functions()

    def _convert_status(self, status):
        # checkbox status is saved as 'on'/'off', same convention as the
        # Simulink mask and the *.json templates (see val_format_conv)
        if status is True:
            return 'on'
        elif status is False:
            return 'off'
        elif status in ['on', 1, '1']:
            return True
        elif status in ['off', 0, '0']:
            return False
        else:
            self.logger.error(f' Value({status}) not supported')
            raise ValueError(f'Value({status}) not supported')

    # *******************************************************************
    # Low-level APIs
    # *******************************************************************
    def get_total_bits(self):
        val = self.ui.total_bits.value()
        self.logger.debug(f'total_bits is {val}')
        return str(val)

    def set_total_bits(self, val):
        self.logger.debug(f'Set total_bits to {val}')
        self.ui.total_bits.setValue(int(val))

    def get_divisions(self):
        val = self.ui.divisions.value()
        self.logger.debug(f'divisions is {val}')
        return str(val)

    def set_divisions(self, val):
        self.logger.debug(f'Set divisions to {val}')
        self.ui.divisions.setValue(int(val))

    def get_size_bits(self):
        val = self.ui.size_bits.value()
        self.logger.debug(f'size_bits is {val}')
        return str(val)

    def set_size_bits(self, val):
        self.logger.debug(f'Set size_bits to {val}')
        self.ui.size_bits.setValue(int(val))

    def get_packing_order(self):
        val = self.ui.packing_order.text()
        self.logger.debug(f'packing_order is {val}')
        return val

    def set_packing_order(self, val):
        self.logger.debug(f'Set packing_order to {val}')
        self.ui.packing_order.setText(str(val))


    # *******************************************************************
    # Validation
    # *******************************************************************
    def validate_config(self):
        """
        Return a list of error messages. The list is empty if the config is valid.

        Ports casper_library/munge_init.m's checks onto this GUI's simplified
        equal-size-division parameter set (total_bits/divisions/size_bits
        instead of casper's divisions/div_size vector): divisions must be a
        positive integer, size_bits must divide evenly into total_bits (this
        GUI only supports the "divisions of equal size" case munge_init.m
        takes when div_size has a single element), and every packing_order
        index must reference a valid division (0 .. divisions-1).
        """
        errors = []
        divisions = self.ui.divisions.value()
        size_bits = self.ui.size_bits.value()
        total_bits = self.ui.total_bits.value()
        if divisions < 1:
            errors.append('Number of Divisions: must be a positive integer.')
        if total_bits != divisions * size_bits:
            errors.append(
                f'Total Bits ({total_bits}) must equal Number of Divisions ({divisions}) '
                f'times Division Size ({size_bits}) = {divisions * size_bits}.')

        raw = str(self.get_packing_order()).strip()
        if raw == '':
            errors.append('Packing Order (division indices, e.g. {3,2,1,0}) must not be empty.')
        else:
            try:
                order = json.loads(raw.replace('{', '[').replace('}', ']'))
                if not isinstance(order, list) or not order:
                    raise ValueError('not a vector')
                if not all(isinstance(i, int) for i in order):
                    raise ValueError('non-integer element')
                if any(i < 0 or i > divisions - 1 for i in order):
                    errors.append(
                        f'Packing Order: every index must be in range 0..{divisions - 1} '
                        f'(matching Number of Divisions).')
            except (ValueError, TypeError):
                errors.append(
                    'Packing Order: must be a bracketed vector of division indices, '
                    'e.g. {3,2,1,0}.')
        return errors

    # *******************************************************************
    # Signal functions
    # *******************************************************************
    def ButtonOK_Clicked(self):
        self.logger.info('---------------------------------------------')
        self.logger.info('Button OK clicked, collecting info...')
        self.logger.info('---------------------------------------------')
        if self.collect_config():
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

    # *******************************************************************
    # Setup Signal functions
    # *******************************************************************
    def setup_signal_functions(self):
        self.ui.button_ok.clicked.connect(self.ButtonOK_Clicked)
        self.ui.button_cancel.clicked.connect(self.ButtonCancel_Clicked)
        self.ui.button_apply.clicked.connect(self.ButtonApply_Clicked)

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
            if k in MUNGE_CONFIG:
                setfunc = MUNGE_CONFIG[k]['set']
                getattr(self, setfunc)(v)

    def collect_config(self):
        """
        Write the config to the target file.
        Return False without writing anything if the config is invalid.
        """
        errors = self.validate_config()
        if errors:
            for e in errors:
                self.logger.error(e)
            QMessageBox.critical(self.winobj, 'Invalid Munge parameters', chr(10).join(errors))
            return False
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Writing config data to {self.target_config}...')
        self.logger.info('-------------------------------------------------')
        try:
            with open(self.target_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            config = {}
            config['parameters'] = {}
            config['parameters']['name'] = ''
            config['parameters']['fullpath'] = ''
            config['parameters']['tag'] = 'dsp:munge'
        for k, v in MUNGE_CONFIG.items():
            getfunc = v['get']
            config['parameters'][k] = str(getattr(self, getfunc)())
        with open(self.target_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True


if __name__ == "__main__":
    parser = ArgumentParser(description="Usage for Munge Mask.")
    parser.add_argument('--template', type=str, dest='template', default=None, help='template config file.')
    parser.add_argument('--target', type=str, dest='target', default='munge.json', help='target config file.')
    parser.add_argument('-l', '--log', type=str, dest='log', default='.', help='The directory for log files.')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true', default=False, help='Turn on verbose.')
    opts = parser.parse_args()
    gen_bconfig(opts.template, opts.target)

    app = QApplication(sys.argv)
    script_path = os.path.realpath(__file__)
    curdir = os.path.dirname(script_path)
    app.setWindowIcon(QIcon(f"{curdir}/icon/casper_icon.png"))
    win = MainWindow()
    op = MungeOperations(win, opts.template, opts.target, opts.log, opts.debug)
    win.show()
    sys.exit(app.exec())
