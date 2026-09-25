import sys, os
import logging
import json
from argparse import ArgumentParser
from pathlib import Path
import shutil

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from rfdc_ui import Ui_MainWindow


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.utils import make_rich_logger, gen_bconfig

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


class _MissingWidgetStub(object):
    """
    Stand-in returned by RFDCOperations._get_qt_obj for a tile/slice/page
    widget name that has no backing object in rfdc_ui.py at all -- a
    handful of these gaps are confirmed to exist (e.g.
    't225_QT_adc3_enable_iq_coarse', 't228_QT_dac1_sample_per_cycle_coarse')
    and, critically, one of them sits on rfdc.json's own DEFAULT config
    path (t228_QT_dac1's default mixer_type is 'Coarse', which
    load_config's stack-page logic switches to on every dialog open) --
    so this can't be treated as a rare user-triggered edge case, it needs
    to degrade gracefully by default. Implements just enough of the Qt
    widget surface this file actually calls (checked via a full grep of
    every obj.<method>(...) / obj.<signal>.connect(...) pattern in this
    module) as safe no-ops / neutral-value reads, so a get/set/signal-
    connect against a missing widget never raises AttributeError.
    """
    def isChecked(self):
        return False

    def setChecked(self, *args, **kwargs):
        pass

    def currentText(self):
        return ''

    def setCurrentText(self, *args, **kwargs):
        pass

    def currentIndex(self):
        return 0

    def setCurrentIndex(self, *args, **kwargs):
        pass

    def value(self):
        return 0

    def setValue(self, *args, **kwargs):
        pass

    def setReadOnly(self, *args, **kwargs):
        pass

    def lineEdit(self):
        return self

    def setText(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def addItem(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        # so `stub.toggled`/`stub.activated`/`stub.editingFinished` (see
        # the properties below) can still be `.connect(...)`-ed as a no-op
        pass

    @property
    def toggled(self):
        return self

    @property
    def activated(self):
        return self

    @property
    def editingFinished(self):
        return self


"""
This class define the signal functions for the GUI.
"""
ADC_TILES = [224, 225, 226, 227]
ADC_DEC_MODE = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 40]
ADC_TILE_ALL_CONFIG = [
    {
        'key':'enable_mts',
        'get': 'get_adc_mts_status',
        'set': 'set_adc_mts_status'
    },
    {
        'key': 'sample_rate',
        'get': 'get_adc_sample_rate',
        'set': 'set_adc_sample_rate'
    },
    {
        'key': 'clk_out',
        'get': 'get_adc_clkout',
        'set': 'set_adc_clkout'
    },
    {
        'key': 'enable_pll',
        'get': 'get_adc_pll_status',
        'set': 'set_adc_pll_status'
    },
    {
        'key': 'ref_clk',
        'get': 'get_adc_refclk',
        'set': 'set_adc_refclk'
    },
    {
        'key': 'axi_stream_clk',
        'get': 'get_adc_req_axis_clk',
        'set': 'set_adc_req_axis_clk'
    },
    {
        'key': 'has_adc_clk',
        'get': 'get_adc_has_clk_status',
        'set': 'set_adc_has_clk_status'
    },
    {
        'key': 'adc_clk_src',
        'get': 'get_adc_clk_src',
        'set': 'set_adc_clk_src'
    },
    {
        'key': 'clk_dist',
        'get': 'get_adc_clk_dist',
        'set': 'set_adc_clk_dist'
    }
]
# DAC tile-level fields: every one of these except 'output_power'/
# 'has_dac_clk'/'dac_clk_src'/'clk_dist' reuses the SAME get/set methods as
# ADC_TILE_ALL_CONFIG verbatim -- tile-level widgets are named 't{tile}_
# {field}' with no adc/dac infix at all (confirmed: t224_enable_mts and
# t228_enable_mts are both plain QCheckBox with identical semantics), so
# get_adc_mts_status(tile)/get_adc_sample_rate(tile)/etc already work
# correctly for DAC tiles unchanged -- they just needed _get_qt_obj's tile
# range widened (see below), not new methods.
DAC_TILE_ALL_CONFIG = [
    {
        'key':'enable_mts',
        'get': 'get_adc_mts_status',
        'set': 'set_adc_mts_status'
    },
    {
        'key': 'sample_rate',
        'get': 'get_adc_sample_rate',
        'set': 'set_adc_sample_rate'
    },
    {
        'key': 'clk_out',
        'get': 'get_adc_clkout',
        'set': 'set_adc_clkout'
    },
    {
        'key': 'enable_pll',
        'get': 'get_adc_pll_status',
        'set': 'set_adc_pll_status'
    },
    {
        'key': 'ref_clk',
        'get': 'get_adc_refclk',
        'set': 'set_adc_refclk'
    },
    {
        'key': 'axi_stream_clk',
        'get': 'get_adc_req_axis_clk',
        'set': 'set_adc_req_axis_clk'
    },
    {
        'key': 'output_power',
        'get': 'get_dac_output_power',
        'set': 'set_dac_output_power'
    },
    {
        'key': 'has_dac_clk',
        'get': 'get_dac_has_clk_status',
        'set': 'set_dac_has_clk_status'
    },
    {
        'key': 'dac_clk_src',
        'get': 'get_dac_clk_src',
        'set': 'set_dac_clk_src'
    },
    {
        'key': 'clk_dist',
        'get': 'get_dac_clk_dist',
        'set': 'set_dac_clk_dist'
    }
]
# DAC slice-level fields (both DT and QT arch share this field list --
# 'datapath_mode' is a real QT-only JSON key but has NO backing widget
# anywhere in rfdc_ui.py, confirmed by exhaustive grep, so it is
# deliberately left out of this list and never touched by collect_config/
# load_config, same treatment as the widget-less 'frame' readout fields).
# Page-suffix convention for DAC is '_bypassed'/'_fine'/'_coarse' (NOT
# ADC's '_real'/'_iq'/'_iq_coarse') -- confirmed via rfdc_ui.py.
DAC_TILE_SEPARATE_CONFIG = [
    {
        'key': 'enable',
        'get': 'get_dt_dac_status',
        'set': 'set_dt_dac_status'
    },
    {
        'key': 'analog_output',
        'get': 'get_dt_dac_analog_output',
        'set': 'set_dt_dac_analog_output'
    },
    {
        'key': 'inter_mode',
        'get': 'get_dt_dac_inter_mode_text',
        'set': 'set_dt_dac_inter_mode'
    },
    {
        'key': 'sample_per_cycle',
        'get': 'get_dt_dac_samples_per_cycle',
        'set': 'set_dt_dac_samples_per_cycle'
    },
    {
        'key': 'req_axis_clk',
        'get': 'get_dt_dac_req_axis_clk',
        'set': 'set_dt_dac_req_axis_clk'
    },
    {
        'key': 'mixer_type',
        'get': 'get_dt_dac_mixer_type',
        'set': 'set_dt_dac_mixer_type'
    },
    {
        'key': 'mixer_mode',
        'get': 'get_dt_dac_mixer_mode',
        'set': 'set_dt_dac_mixer_mode'
    },
    {
        'key': 'coarse_freq',
        'get': 'get_dt_dac_coarse_freq',
        'set': 'set_dt_dac_coarse_freq'
    },
    {
        'key': 'nco_freq',
        'get': 'get_dt_dac_nco_freq',
        'set': 'set_dt_dac_nco_freq'
    },
    {
        'key': 'nco_phase',
        'get': 'get_dt_dac_nco_phase',
        'set': 'set_dt_dac_nco_phase'
    },
    {
        'key': 'nyquist_zone',
        'get': 'get_dt_dac_nyquist_zone',
        'set': 'set_dt_dac_nyquist_zone'
    },
    {
        'key': 'decode_mode',
        'get': 'get_dt_dac_decode_mode',
        'set': 'set_dt_dac_decode_mode'
    }
]
ADC_TILE_SEPARATE_CONFIG = [
    {
        'key': 'enable',
        'get': 'get_dt_adc_status',
        'set': 'set_dt_adc_status'
    },
    {
        'key': 'digital_output',
        'get': 'get_dt_adc_digital_output',
        'set': 'set_dt_adc_digital_output'
    },
    {
        'key': 'dec_mode',
        'get': 'get_dt_adc_dec_mode_text',
        'set': 'set_dt_adc_dec_mode'
    },
    {
        'key': 'sample_per_cycle',
        'get': 'get_dt_adc_samples_per_cycle',
        'set': 'set_dt_adc_samples_per_cycle'
    },
    {
        'key': 'req_axis_clk',
        'get': 'get_dt_adc_req_axis_clk',
        'set': 'set_dt_adc_req_axis_clk'
    },
    {
        'key': 'mixer_type',
        'get': 'get_dt_adc_mixer_type',
        'set': 'set_dt_adc_mixer_type'
    },
    {
        'key': 'mixer_mode',
        'get': 'get_dt_adc_mixer_mode',
        'set': 'set_dt_adc_mixer_mode'
    },
    {
        'key': 'coarse_freq',
        'get': 'get_dt_adc_coarse_freq',
        'set': 'set_dt_adc_coarse_freq'
    },
    {
        'key': 'nco_freq',
        'get': 'get_dt_adc_nco_freq',
        'set': 'set_dt_adc_nco_freq'
    },
    {
        'key': 'nco_phase',
        'get': 'get_dt_adc_nco_phase',
        'set': 'set_dt_adc_nco_phase'
    },
    {
        'key': 'nyquist_zone',
        'get': 'get_dt_adc_nyquist_zone',
        'set': 'set_dt_adc_nyquist_zone'
    },
    {
        'key': 'cal_mode',
        'get': 'get_dt_adc_cal_mode',
        'set': 'set_dt_adc_cal_mode'
    }
]
DAC_TILES = [228, 229, 230, 231]
class RFDCOperations(object):
    def __init__(self, winobj, template_config='rfdc.json', target_config='rfdc.json', logdir='.', debug=False):
        if debug:
            self.logger = make_rich_logger('rfdc.log', logging.DEBUG, mode='a', logdir=logdir)
        else:
            self.logger = make_rich_logger('rfdc.log', logging.ERROR, mode='a', logdir=logdir)
        self.logger.info('*************************************************')
        self.logger.info('RFDC Mask started.')
        self.logger.info('*************************************************')
        self.logger.info(f'Template config file is {template_config}.')
        self.logger.info(f'Target config file is {target_config}.')
        self.template_config = template_config
        self.target_config = target_config
        self.winobj = winobj
        self.ui = winobj.ui
        self.load_config()
        self.setup_signal_functions()

    def _get_qt_obj(self, tile, name, adc=None, DQ=None, kind='adc'):
        """
        Docstring for _get_qt_obj:
            get the QT object.
        :param tile (uint8) : tile number (ADC: 224-227, DAC: 228-231).
        :param name (str)   : object name.
        :param adc  (uint8) : slice ID - 0/1 for Dual Tile, 0-3 for Quad Tile.
        :param DQ   (str)   : Dual Tile(DT) or Quad Tile(QT).
        :param kind (str)   : 'adc' or 'dac' -- selects the widget-name
                               infix (t{tile}_{DQ}_adc{n}_.../
                               t{tile}_{DQ}_dac{n}_...). Ignored (and safe
                               to leave at its default) when adc is None,
                               since tile-level widget names never carry an
                               adc/dac infix.
        """
        if tile not in ADC_TILES and tile not in DAC_TILES:
            self.logger.error(f'Tile{tile} is not a valid RFDC tile')
            raise ValueError(f'Tile{tile} is not a valid RFDC tile')
        objname = f't{tile}_{name}' if adc == None else f't{tile}_{DQ}_{kind}{adc}_{name}'
        try:
            return getattr(self.ui, objname)
        except AttributeError:
            # confirmed gap in rfdc_ui.py (no backing widget at all for
            # this tile/slice/page combination) -- see _MissingWidgetStub's
            # docstring for why this must degrade gracefully rather than
            # raise, even on the default config.
            self.logger.warning(f'{objname} has no widget in rfdc_ui.py -- using a no-op stub.')
            return _MissingWidgetStub()
    
    def _convert_status(self, status):
        if status == True:
            return 'on'
        elif status == False:
            return 'off'
        elif status == 'on':
            return True
        elif status == 'off':
            return False
        
    def get_tile_status(self, tile):
        """
        Docstring for get_tile_status:
            get the tile status.

        :param tile (uint8) : tile number.
        """
        # This function is a little bit different,
        # as the obj name is different from others.
        if tile not in ADC_TILES and tile not in DAC_TILES:
            self.logger.error('Tile{tile} is not valid.')
            raise ValueError('Tile{tile} is not valid.')
        obj = getattr(self.ui, f'Tile{tile}_enable')
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile} status is {status}.')
        return self._convert_status(status)

    def set_title_status(self, tile, status):
        """
        Docstring for set_title_status
        
        :param tile (uint8) : tile number.
        :param status(bool or str): status. 
        """
        self.logger.debug(f'Set Tile{tile} Status to {status}.')
        if status == 'on' or status == 'off':
            status = self._convert_status(status)
        obj = getattr(self.ui, f'Tile{tile}_enable')
        obj.setChecked(status)

    def get_adc_mts_status(self, tile):
        """
        Docstring for get_adc_mts:
            get the status of adc mts.
        
        :param tile (uint8) : tile number.
        """
        obj = self._get_qt_obj(tile, 'enable_mts')
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile} MTS status is {status}')
        return self._convert_status(status)
    
    def set_adc_mts_status(self, tile, status):
        """
        Docstring for set_adc_mts_status
        
        :param tile (uint8) : tile number.
        :param tile (str)   : 'on' or 'off'.
        """
        self.logger.debug(f'Set Tile{tile} MTS status to {status}.')
        if status == 'on' or status == 'off':
            status = self._convert_status(status)
        obj = self._get_qt_obj(tile, 'enable_mts')
        obj.setChecked(status)


    def get_adc_sample_rate(self, tile):
        """
        Docstring for get_adc_sample_rate:
            get the adc sampling rate.
        :param tile (uint8) : tile number.
        """
        obj = self._get_qt_obj(tile, 'sample_rate')
        samplerate = obj.value()
        self.logger.debug(f'Sampling Rate of Tile{tile} ADC: {samplerate}MHz')
        return samplerate
    
    def set_adc_sample_rate(self, tile, freq):
        """
        Docstring for set_adc_sample_rate
        
        :param tile (uint8) : tile number.
        :param freq (float or str) : frequency in MHz.
        """
        self.logger.debug(f'Set Tile{tile} ADC Sampling Rate to {freq} MHz.')
        obj = self._get_qt_obj(tile, 'sample_rate')
        obj.setValue(float(freq))
        
    def get_adc_pll_status(self, tile):
        """
        Docstring for get_adc_pll_status:
            get the adc pll status.
        
        :param tile (uint8): tile number.
        """
        obj = self._get_qt_obj(tile, 'enable_pll')
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile} PLL status is {status}')
        return self._convert_status(status)
    
    def set_adc_pll_status(self, tile, status):
        """
        Docstring for set_adc_pll_status
        
        :param self: Description
        :param tile (uint8) : tile number.
        :param tile (str)   : 'on' or 'off'.
        """
        self.logger.debug(f'Set Tile{tile} ADC PLL status to {status}.')
        if status == 'on' or status == 'off':
            status = self._convert_status(status)
        obj = self._get_qt_obj(tile, 'enable_pll')
        obj.setChecked(status)
    
    def get_adc_refclk(self, tile):
        """
        Docstring for get_adc_refclk:
            get the adc reference clk freqency.
        
        :param tile (uint8): tile number.
        """
        obj = self._get_qt_obj(tile, 'ref_clk')
        refclk = obj.currentText()
        self.logger.debug(f'Tile{tile} Ref Clock freq is {refclk} MHz.')
        return float(refclk)
    
    def set_adc_refclk(self, tile, freq):
        """
        Docstring for set_adc_refclk
        
        :param tile (uint8) : tile number.
        :param freq (float or str) : frequency in MHz.
        """
        self.logger.debug(f'Set Tile{tile} ADC Ref Clock to {freq} MHz.')
        obj = self._get_qt_obj(tile, 'ref_clk')
        obj.setCurrentText(str(freq))
    
    def get_adc_req_axis_clk(self, tile):
        """
        Docstring for get_req_axis_clk:
            get the required axi4 stream clock frequency.
        
        :param tile (uint8): tile number.
        """
        obj = self._get_qt_obj(tile, 'axi_stream_clk')
        clkfreq = obj.value()
        self.logger.debug(f'Tile{tile} required axis clock is {clkfreq} MHz')
        return clkfreq
        
    def set_adc_req_axis_clk(self, tile, freq):
        """
        Docstring for set_req_axis_clk:
            set the required axi4 stream clock freq.

        :param tile (uint8) : tile number.
        :param freq (str) : the frequency in MHz.
        """
        self.logger.debug(f'Set Tile{tile} required axis clk frequency to {freq} MHz.')
        obj = self._get_qt_obj(tile, 'axi_stream_clk')
        obj.setReadOnly(True)
        obj.lineEdit().setText(str(freq))

    def get_adc_clkout(self, tile):
        """
        Docstring for get_adc_clkout
        
        :param tile     (uint8) : tile number.
        :param tile: Description
        """
        obj = self._get_qt_obj(tile, 'clk_out')
        value = obj.currentText()
        self.logger.debug(f'ADC clock out of Tile{tile} is {value}.')
        return value

    def set_adc_clkout_list(self, tile, values, default=0):
        """
        Docstring for set_adc_clkout_list:
            set the adc clkout freq.
        :param tile     (uint8) : tile number.
        :param values   (list)  : the values for adc_clkout
        """
        self.logger.debug(f'ADC clock out of Tile{tile} is {values}.')
        self.logger.debug(f'Default ADC clock out is {values[default]}MHz.')
        obj = self._get_qt_obj(tile, 'clk_out')
        obj.clear()
        for i in range(len(values)):
            obj.addItem(str(values[i]), i)
        obj.setCurrentIndex(default)
    
    def set_adc_clkout(self, tile, val):
        """
        Docstring for set_adc_clkout
        
        Docstring for set_adc_clkout_list:
            set the adc clkout freq.
        :param tile     (uint8) : tile number.
        :param val      (str)   : the adc_clkout val
        """
        self.logger.debug(f'ADC clock out of Tile{tile} is {val}.')
        obj = self._get_qt_obj(tile, 'clk_out')
        obj.setCurrentText(str(val))

    def get_adc_has_clk_status(self, tile):
        obj = self._get_qt_obj(tile, 'has_adc_clk')
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile} has_adc_clk status is {status}')
        return self._convert_status(status)

    def set_adc_has_clk_status(self, tile, status):
        if status == 'on' or status == 'off':
            status = self._convert_status(status)
        obj = self._get_qt_obj(tile, 'has_adc_clk')
        obj.setChecked(status)

    def get_adc_clk_src(self, tile):
        obj = self._get_qt_obj(tile, 'adc_clk_src')
        return obj.currentText()

    def set_adc_clk_src(self, tile, val):
        obj = self._get_qt_obj(tile, 'adc_clk_src')
        obj.setCurrentText(str(val))

    def get_adc_clk_dist(self, tile):
        obj = self._get_qt_obj(tile, 'clk_dist')
        return obj.currentText()

    def set_adc_clk_dist(self, tile, val):
        obj = self._get_qt_obj(tile, 'clk_dist')
        obj.setCurrentText(str(val))

    def get_dac_output_power(self, tile):
        obj = self._get_qt_obj(tile, 'output_power')
        return obj.value()

    def set_dac_output_power(self, tile, val):
        obj = self._get_qt_obj(tile, 'output_power')
        obj.setValue(float(val))

    def get_dac_has_clk_status(self, tile):
        obj = self._get_qt_obj(tile, 'has_dac_clk')
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile} has_dac_clk status is {status}')
        return self._convert_status(status)

    def set_dac_has_clk_status(self, tile, status):
        if status == 'on' or status == 'off':
            status = self._convert_status(status)
        obj = self._get_qt_obj(tile, 'has_dac_clk')
        obj.setChecked(status)

    def get_dac_clk_src(self, tile):
        obj = self._get_qt_obj(tile, 'dac_clk_src')
        return obj.currentText()

    def set_dac_clk_src(self, tile, val):
        obj = self._get_qt_obj(tile, 'dac_clk_src')
        obj.setCurrentText(str(val))

    def get_dac_clk_dist(self, tile):
        obj = self._get_qt_obj(tile, 'clk_dist')
        return obj.currentText()

    def set_dac_clk_dist(self, tile, val):
        obj = self._get_qt_obj(tile, 'clk_dist')
        obj.setCurrentText(str(val))

    def get_dt_adc_status(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_status
        
        :param tile (uint8): tile number
        :param adc. (uin8) : adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'enable_real'
            targets.append('enable_iq')
            targets.append('enable_iq_coarse')
        elif page == 1:
            source = 'enable_iq'
            targets.append('enable_real')
            targets.append('enable_iq_coarse')
        elif page == 2:
            source ='enable_iq_coarse'
            targets.append('enable_real')
            targets.append('enable_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile}.ADC{adc}(Dual Tile) status is {status}.')
        # also set the other status for sync
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setChecked(status)
        return self._convert_status(status)
    
    def set_dt_adc_status(self, tile, adc, status, DQ='DT'):
        """
        Docstring for set_dt_adc_status
        
        :param tile     (uint8) : tile number.
        :param adc      (uint8) : adc id - 0 or 1.
        :param status   (str)  : 'on' or 'off'.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc}(Dual Tile) status to {status}.')
        if status == 'on' or status == 'off':
            status = self._convert_status(status)
        # we will set the status on all of the three pages
        targets = ['enable_real', 
                   'enable_iq', 
                   'enable_iq_coarse']
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setChecked(status)

    def get_dt_adc_digital_output(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_digital_output
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'digital_output_real'
            targets.append('digital_output_iq')
            targets.append('digital_output_iq_coarse')
        elif page == 1:
            source = 'digital_output_iq'
            targets.append('digital_output_real')
            targets.append('digital_output_iq_coarse')
        elif page == 2:
            source = 'digital_output_iq_coarse'
            targets.append('digital_output_real')
            targets.append('digital_output_iq_coarse')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        val = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) digital output is {val}.')
        # also set the other status for sync
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(val))
        return val
    
    def set_dt_adc_digital_output(self, tile, adc, val, DQ='DT'):
        """
        Docstring for set_dt_adc_digital_output
        
        :param tile     (uint8) : tile number.
        :param adc      (uint8) : adc id - 0 or 1.
        :param val      (str)   : 'Real' or ''I/Q.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{tile} (Dual Tile) digital output to {val}.')
        # we will set the status on all of the three pages
        targets = ['digital_output_real', 
                   'digital_output_iq', 
                   'digital_output_iq_coarse']
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(val))

    def get_dt_adc_dec_mode(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_dec_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'dec_mode_real'
            targets.append('dec_mode_iq')
            targets.append('dec_mode_iq_coarse')
        elif page == 1:
            source = 'dec_mode_iq'
            targets.append('dec_mode_real')
            targets.append('dec_mode_iq_coarse')
        elif page == 2:
            source = 'dec_mode_iq_coarse'
            targets.append('dec_mode_real')
            targets.append('dec_mode_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        decmode = obj.currentIndex()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) DEC mode is x{ADC_DEC_MODE[decmode]}.')
        # also set the other value for sync
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentIndex(decmode)
        return ADC_DEC_MODE[decmode]

    def get_dt_adc_dec_mode_text(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_dec_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'dec_mode_real'
            targets.append('dec_mode_iq')
            targets.append('dec_mode_iq_coarse')
        elif page == 1:
            source = 'dec_mode_iq'
            targets.append('dec_mode_real')
            targets.append('dec_mode_iq_coarse')
        elif page == 2:
            source = 'dec_mode_iq_coarse'
            targets.append('dec_mode_real')
            targets.append('dec_mode_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        decmode = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) DEC mode is decmode].')
        # also set the other value for sync
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(decmode))
        return decmode

    def set_dt_adc_dec_mode(self, tile, adc, decmode, DQ='DT'):
        """
        Docstring for set_dt_adc_dec_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param decmode (str or int): dec mode
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} DEC Mode to {decmode}.')
        targets = ['dec_mode_real',
                   'dec_mode_iq',
                   'dec_mode_iq_coarse']
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, DQ)
            if isinstance(decmode, int):
                obj.setCurrentIndex(decmode)
            elif isinstance(decmode, str):
                obj.setCurrentText(str(decmode))
            else:
                self.logger.error(f'decmode({decmode}) is not supported.')
    
    def get_dt_adc_samples_per_cycle(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_samples_per_cycle
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'sample_per_cycle_real'
            targets.append('sample_per_cycle_iq')
            targets.append('sample_per_cycle_iq_coarse')
        elif page == 1:
            source = 'sample_per_cycle_iq'
            targets.append('sample_per_cycle_real')
            targets.append('sample_per_cycle_iq_coarse')
        elif page == 2:
            source = 'sample_per_cycle_iq_coarse'
            targets.append('sample_per_cycle_real')
            targets.append('sample_per_cycle_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        spc = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) samples per cycle is {spc}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(spc))
        return int(spc)
    
    def set_dt_adc_samples_per_cycle(self, tile, adc, spc, DQ='DT'):
        """
        Docstring for set_dt_adc_samples_per_cycle
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param spc  (uint8): samples per cycle.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} (Dual Tile) samples per cycle to {spc}.')
        targets = ['sample_per_cycle_real',
                   'sample_per_cycle_iq',
                   'sample_per_cycle_iq_coarse']
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, DQ)
        obj.setCurrentText(str(spc))

    def get_dt_adc_req_axis_clk(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_req_axis_clk
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'req_axis_clk_real'
            targets.append('req_axis_clk_iq')
            targets.append('req_axis_clk_iq_coarse')
        elif page == 1:
            source = 'req_axis_clk_iq'
            targets.append('req_axis_clk_real')
            targets.append('req_axis_clk_iq_coarse')
        elif page == 2:
            source = 'req_axis_clk_iq_coarse'
            targets.append('req_axis_clk_real')
            targets.append('req_axis_clk_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        value = obj.value()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile)  required axis clock is {value}MHz.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setValue(value)
        return value

    def set_dt_adc_req_axis_clk(self, tile, adc, freq, DQ='DT'):
        """
        Docstring for set_dt_adc_req_axis_clk
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param freq (float or str): the clock freqency.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} (Dual Tile) required axi4 stream clock to {freq} MHz.')
        targets = ['req_axis_clk_real', 
                   'req_axis_clk_iq',
                   'req_axis_clk_iq_coarse']
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setValue(float(freq))

    def get_dt_adc_mixer_type(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_mixer_type
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'mixer_type_real'
            #targets.append('mixer_type_iq')
            #targets.append('mixer_type_iq_coarse')
        elif page == 1:
            source = 'mixer_type_iq'
            #targets.append('mixer_type_real')
            targets.append('mixer_type_iq_coarse')
        elif page == 2:
            source = 'mixer_type_iq_coarse'
            #targets.append('mixer_type_real')
            targets.append('mixer_type_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        mixertype = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Mixer Type is {mixertype}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixertype))
        return mixertype

    def set_dt_adc_mixer_type(self, tile, adc, mixertype, DQ='DT'):
        """
        Docstring for set_dt_adc_mixer_type
        
        :param tile     (uint8) : tile number
        :param adc      (uint8) : adc id - 0 or 1.
        :param mixertype(str)   : mixer type.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} Mixer Type to {mixertype}.')
        # It depends on what the mixertype is
        if mixertype == 'Bypassed':
            targets = ['mixer_type_real']
        elif mixertype == 'Fine' or mixertype == 'Coarse':
            targets = ['mixer_type_iq',
                       'mixer_type_iq_coarse']
        else:
            self.logger.error(f'mixtertype{mixertype} is not supported.')
            raise ValueError(f'mixtertype{mixertype} is not supported.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixertype))

    def get_dt_adc_mixer_mode(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_mixer_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'mixer_mode_real'
            #targets.append('mixer_mode_iq')
            #targets.append('mixer_mode_iq_coarse')
        elif page == 1:
            source = 'mixer_mode_iq'
            targets.append('mixer_mode_real')
            targets.append('mixer_mode_iq_coarse')
        elif page == 2:
            source = 'mixer_mode_iq_coarse'
            targets.append('mixer_mode_real')
            targets.append('mixer_mode_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        mixermode = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Mixer Type is {mixermode}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixermode))
        return mixermode
    
    def set_dt_adc_mixer_mode(self, tile, adc, mixermode, DQ='DT'):
        """
        Docstring for set_dt_adc_mixer_mode
        
        :param tile     (uint8) : tile number
        :param adc      (uint8) : adc id - 0 or 1.
        :param mixermode(str)   : mixer mode
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} Mixer Mode to {mixermode}.')
        if mixermode == 'Real -> Real':
            targets = ['mixer_mode_real',
                       'mixer_mode_iq',
                       'mixer_mode_iq_coarse']
        elif mixermode == 'Real -> I/Q':
            targets = ['mixer_mode_iq',
                       'mixer_mode_iq_coarse']
        else:
            self.logger.error(f'mixermode{mixermode} is not supported.')
            raise ValueError(f'mixermode{mixermode} is not supported.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixermode))
        
    def get_dt_adc_nco_freq(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_nco_freq
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'nco_freq_iq', adc, DQ)
        ncofreq = obj.value()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) NCO Freq is {ncofreq} GHz.')
        return ncofreq
    
    def set_dt_adc_nco_freq(self, tile, adc, ncofreq, DQ='DT'):
        """
        Docstring for set_dt_adc_nco_freq
        
        :param tile     (uint8): tile number
        :param adc      (uint8): adc id - 0 or 1.
        :param ncofreq  (float or str): nco frequency in GHz.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} NCO Freqnency to {ncofreq} GHz.')
        obj = self._get_qt_obj(tile, 'nco_freq_iq', adc, DQ)
        obj.setValue(float(ncofreq))

    def get_dt_adc_nco_phase(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_nco_phase
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'nco_phase_iq', adc, DQ)
        ncophase = obj.value()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) NCO Phase is {ncophase}.')
        return ncophase

    def set_dt_adc_nco_phase(self, tile, adc, ncophase, DQ='DT'):
        """
        Docstring for set_dt_adc_nco_phase
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param ncophase (float or str): nco phase.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} NCO Phase to {ncophase}.')
        obj = self._get_qt_obj(tile, 'nco_phase_iq', adc, DQ)
        obj.setValue(float(ncophase))

    def get_dt_adc_coarse_freq(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_coarse_freq
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'coarse_freq', adc, DQ)
        freq = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Coarse Freq is {freq}MHz.')
        return freq

    def set_dt_adc_coarse_freq(self, tile, adc, freq, DQ='DT'):
        """
        Docstring for set_dt_adc_coarse_freq
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param freq (str)  : coarse frequency in ??
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} Coarse Frequency to {freq}.')
        obj = self._get_qt_obj(tile, 'coarse_freq', adc, DQ)
        obj.setCurrentText(str(freq))

    def get_dt_adc_nyquist_zone(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_nyquist_zone
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'nyquist_zone_real'
            targets.append('nyquist_zone_iq')
            targets.append('nyquist_zone_iq_coarse')
        elif page == 1:
            source = 'nyquist_zone_iq'
            targets.append('nyquist_zone_real')
            targets.append('nyquist_zone_iq_coarse')
        elif page == 2:
            source = 'nyquist_zone_iq_coarse'
            targets.append('nyquist_zone_real')
            targets.append('nyquist_zone_iq')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        nzone = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Nyquist Zone is {nzone}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(nzone))
        return nzone

    def set_dt_adc_nyquist_zone(self, tile, adc, nzone, DQ='DT'):
        """
        Docstring for set_dt_adc_nyquist_zone
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param nzone (str): nyquist zone
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} Nyquist Zone to {nzone}.')
        if nzone not in ['Zone 1', 'Zone 2']:
            self.logger.error(f'nzone({nzone}) is not supported.')
            raise ValueError(f'nzone({nzone}) is not supported.')
        targets = ['nyquist_zone_real',
                   'nyquist_zone_iq',
                   'nyquist_zone_iq_coarse']
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(nzone))

    def get_dt_adc_cal_mode(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_cal_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc, DQ)
        # we need to get the value based on the page
        targets = []
        if page == 0:
            source = 'cal_mode_real'
            targets.append('cal_mode_iq')
            targets.append('cal_mode_iq_coarse')
        elif page == 1:
            source = 'cal_mode_iq'
            targets.append('cal_mode_real')
            targets.append('cal_mode_iq_coarse')
        elif page == 2:
            source = 'cal_mode_iq_coarse'
            targets.append('cal_mode_real')
            targets.append('cal_mode_iq_coarse')
        obj = self._get_qt_obj(tile, source, adc, DQ)
        calmode = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Calibration Mode is {calmode}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(calmode))
        return calmode

    def set_dt_adc_cal_mode(self, tile, adc, calmode, DQ='DT'):
        """
        Docstring for set_dt_adc_cal_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param calmode (str): calibration mode.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} Calibration Mode to {calmode}.')
        if calmode not in ['Mode 1', 'Mode 2']:
            self.logger.error(f'calmode{calmode} is not supported.')
            raise ValueError(f'calmode{calmode} is not supported.')
        targets = ['cal_mode_real',
                   'cal_mode_iq',
                   'cal_mode_iq_coarse']
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, adc, DQ)
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(calmode))
        
    def get_dt_adc_stack_page(self, tile, adc, DQ='DT'):
        """
        Docstring for get_dt_adc_stack_page
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'stackedwidget', adc, DQ)
        page = obj.currentIndex()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) stack page is {page}.')
        return page

    def set_dt_adc_stack_page(self, tile, adc, page, DQ='DT'):
        """
        Docstring for set_dt_adc_stack_page
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param page (uint8): page id - 0 or 1.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} (Dual Tile) stack page to {page}.')
        obj = self._get_qt_obj(tile, 'stackedwidget', adc, DQ)
        obj.setCurrentIndex(page)

    # -------------------------------------------------------------------
    # DAC slice-level accessors (Dual Tile by default, DQ='QT' for Quad
    # Tile -- mirrors the get_dt_adc_*/set_dt_adc_* structure above, but
    # DAC's page-suffix convention is '_bypassed'/'_fine'/'_coarse' (not
    # ADC's '_real'/'_iq'/'_iq_coarse') and several field names differ
    # (analog_output not digital_output, inter_mode not dec_mode,
    # decode_mode instead of cal_mode -- confirmed against rfdc_ui.py).
    # -------------------------------------------------------------------
    def get_dt_dac_status(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'enable_bypassed'
            targets = ['enable_fine', 'enable_coarse']
        elif page == 1:
            source = 'enable_fine'
            targets = ['enable_bypassed', 'enable_coarse']
        elif page == 2:
            source = 'enable_coarse'
            targets = ['enable_bypassed', 'enable_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) status is {status}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setChecked(status)
        return self._convert_status(status)

    def set_dt_dac_status(self, tile, dac, status, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) status to {status}.')
        if status == 'on' or status == 'off':
            status = self._convert_status(status)
        for t in ['enable_bypassed', 'enable_fine', 'enable_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setChecked(status)

    def get_dt_dac_analog_output(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'analog_output_bypassed'
            targets = ['analog_output_fine', 'analog_output_coarse']
        elif page == 1:
            source = 'analog_output_fine'
            targets = ['analog_output_bypassed', 'analog_output_coarse']
        elif page == 2:
            source = 'analog_output_coarse'
            targets = ['analog_output_bypassed', 'analog_output_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        val = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) analog output is {val}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(val))
        return val

    def set_dt_dac_analog_output(self, tile, dac, val, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) analog output to {val}.')
        for t in ['analog_output_bypassed', 'analog_output_fine', 'analog_output_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(val))

    def get_dt_dac_inter_mode_text(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'inter_mode_bypassed'
            targets = ['inter_mode_fine', 'inter_mode_coarse']
        elif page == 1:
            source = 'inter_mode_fine'
            targets = ['inter_mode_bypassed', 'inter_mode_coarse']
        elif page == 2:
            source = 'inter_mode_coarse'
            targets = ['inter_mode_bypassed', 'inter_mode_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        val = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) inter mode is {val}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(val))
        return val

    def set_dt_dac_inter_mode(self, tile, dac, val, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) inter mode to {val}.')
        for t in ['inter_mode_bypassed', 'inter_mode_fine', 'inter_mode_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(val))

    def get_dt_dac_samples_per_cycle(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'sample_per_cycle_bypassed'
            targets = ['sample_per_cycle_fine', 'sample_per_cycle_coarse']
        elif page == 1:
            source = 'sample_per_cycle_fine'
            targets = ['sample_per_cycle_bypassed', 'sample_per_cycle_coarse']
        elif page == 2:
            source = 'sample_per_cycle_coarse'
            targets = ['sample_per_cycle_bypassed', 'sample_per_cycle_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        spc = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) samples per cycle is {spc}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(spc))
        return int(spc)

    def set_dt_dac_samples_per_cycle(self, tile, dac, spc, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) samples per cycle to {spc}.')
        for t in ['sample_per_cycle_bypassed', 'sample_per_cycle_fine', 'sample_per_cycle_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(spc))

    def get_dt_dac_req_axis_clk(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'req_axis_clk_bypassed'
            targets = ['req_axis_clk_fine', 'req_axis_clk_coarse']
        elif page == 1:
            source = 'req_axis_clk_fine'
            targets = ['req_axis_clk_bypassed', 'req_axis_clk_coarse']
        elif page == 2:
            source = 'req_axis_clk_coarse'
            targets = ['req_axis_clk_bypassed', 'req_axis_clk_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        value = obj.value()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) required axis clock is {value}MHz.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setValue(value)
        return value

    def set_dt_dac_req_axis_clk(self, tile, dac, freq, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) required axi4 stream clock to {freq} MHz.')
        for t in ['req_axis_clk_bypassed', 'req_axis_clk_fine', 'req_axis_clk_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setValue(float(freq))

    def get_dt_dac_mixer_type(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'mixer_type_bypassed'
        elif page == 1:
            source = 'mixer_type_fine'
            targets = ['mixer_type_coarse']
        elif page == 2:
            source = 'mixer_type_coarse'
            targets = ['mixer_type_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        mixertype = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) Mixer Type is {mixertype}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixertype))
        return mixertype

    def set_dt_dac_mixer_type(self, tile, dac, mixertype, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) Mixer Type to {mixertype}.')
        if mixertype == 'Bypassed':
            targets = ['mixer_type_bypassed']
        elif mixertype == 'Fine' or mixertype == 'Coarse':
            targets = ['mixer_type_fine', 'mixer_type_coarse']
        else:
            self.logger.error(f'mixertype({mixertype}) is not supported.')
            raise ValueError(f'mixertype({mixertype}) is not supported.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixertype))

    def get_dt_dac_mixer_mode(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'mixer_mode_bypassed'
        elif page == 1:
            source = 'mixer_mode_fine'
            targets = ['mixer_mode_bypassed', 'mixer_mode_coarse']
        elif page == 2:
            source = 'mixer_mode_coarse'
            targets = ['mixer_mode_bypassed', 'mixer_mode_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        mixermode = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) Mixer Mode is {mixermode}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixermode))
        return mixermode

    def set_dt_dac_mixer_mode(self, tile, dac, mixermode, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) Mixer Mode to {mixermode}.')
        if mixermode == 'Real -> Real':
            targets = ['mixer_mode_bypassed', 'mixer_mode_fine', 'mixer_mode_coarse']
        elif mixermode == 'I/Q -> Real':
            targets = ['mixer_mode_fine', 'mixer_mode_coarse']
        else:
            self.logger.error(f'mixermode({mixermode}) is not supported.')
            raise ValueError(f'mixermode({mixermode}) is not supported.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(mixermode))

    def get_dt_dac_nco_freq(self, tile, dac, DQ='DT'):
        obj = self._get_qt_obj(tile, 'nco_freq', dac, DQ, kind='dac')
        ncofreq = obj.value()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) NCO Freq is {ncofreq} GHz.')
        return ncofreq

    def set_dt_dac_nco_freq(self, tile, dac, ncofreq, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) NCO Freqency to {ncofreq} GHz.')
        obj = self._get_qt_obj(tile, 'nco_freq', dac, DQ, kind='dac')
        obj.setValue(float(ncofreq))

    def get_dt_dac_nco_phase(self, tile, dac, DQ='DT'):
        obj = self._get_qt_obj(tile, 'nco_phase', dac, DQ, kind='dac')
        ncophase = obj.value()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) NCO Phase is {ncophase}.')
        return ncophase

    def set_dt_dac_nco_phase(self, tile, dac, ncophase, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) NCO Phase to {ncophase}.')
        obj = self._get_qt_obj(tile, 'nco_phase', dac, DQ, kind='dac')
        obj.setValue(float(ncophase))

    def get_dt_dac_coarse_freq(self, tile, dac, DQ='DT'):
        # Unlike ADC's bare (unsuffixed) coarse_freq widget, DAC's
        # coarse_freq is page-suffixed with only '_fine'/'_coarse' variants
        # -- there is no '_bypassed' widget (the concept doesn't apply when
        # the mixer is bypassed), confirmed against rfdc_ui.py. Page 0
        # falls back to reading/syncing the 'fine' widget.
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        source = 'coarse_freq_coarse' if page == 2 else 'coarse_freq_fine'
        target = 'coarse_freq_fine' if page == 2 else 'coarse_freq_coarse'
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        freq = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) Coarse Freq is {freq}MHz.')
        obj2 = self._get_qt_obj(tile, target, dac, DQ, kind='dac')
        obj2.setCurrentText(str(freq))
        return freq

    def set_dt_dac_coarse_freq(self, tile, dac, freq, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) Coarse Frequency to {freq}.')
        for t in ['coarse_freq_fine', 'coarse_freq_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(freq))

    def get_dt_dac_nyquist_zone(self, tile, dac, DQ='DT'):
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        targets = []
        if page == 0:
            source = 'nyquist_zone_bypassed'
            targets = ['nyquist_zone_fine', 'nyquist_zone_coarse']
        elif page == 1:
            source = 'nyquist_zone_fine'
            targets = ['nyquist_zone_bypassed', 'nyquist_zone_coarse']
        elif page == 2:
            source = 'nyquist_zone_coarse'
            targets = ['nyquist_zone_bypassed', 'nyquist_zone_fine']
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        nzone = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) Nyquist Zone is {nzone}.')
        for t in targets:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(nzone))
        return nzone

    def set_dt_dac_nyquist_zone(self, tile, dac, nzone, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) Nyquist Zone to {nzone}.')
        for t in ['nyquist_zone_bypassed', 'nyquist_zone_fine', 'nyquist_zone_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(nzone))

    def get_dt_dac_decode_mode(self, tile, dac, DQ='DT'):
        # decode_mode has no '_fine' page widget in rfdc_ui.py (only
        # '_bypassed'/'_coarse' exist) -- page 1 (Fine mixer) falls back to
        # reading/syncing the 'coarse' widget, the nearest still-existing
        # IQ-mode variant.
        page = self.get_dt_dac_stack_page(tile, dac, DQ)
        source = 'decode_mode_bypassed' if page == 0 else 'decode_mode_coarse'
        target = 'decode_mode_coarse' if page == 0 else 'decode_mode_bypassed'
        obj = self._get_qt_obj(tile, source, dac, DQ, kind='dac')
        decmode = obj.currentText()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) Decode Mode is {decmode}.')
        obj2 = self._get_qt_obj(tile, target, dac, DQ, kind='dac')
        obj2.setCurrentText(str(decmode))
        return decmode

    def set_dt_dac_decode_mode(self, tile, dac, decmode, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) Decode Mode to {decmode}.')
        for t in ['decode_mode_bypassed', 'decode_mode_coarse']:
            try:
                obj = self._get_qt_obj(tile, t, dac, DQ, kind='dac')
            except AttributeError:
                self.logger.debug(f'Tile{tile} slice widget for sync target is missing (known rfdc_ui.py gap) -- skipping.')
                continue
            obj.setCurrentText(str(decmode))

    def get_dt_dac_stack_page(self, tile, dac, DQ='DT'):
        obj = self._get_qt_obj(tile, 'stackedwidget', dac, DQ, kind='dac')
        page = obj.currentIndex()
        self.logger.debug(f'Tile{tile}.DAC{dac} ({DQ}) stack page is {page}.')
        return page

    def set_dt_dac_stack_page(self, tile, dac, page, DQ='DT'):
        self.logger.debug(f'Set Tile{tile}.DAC{dac} ({DQ}) stack page to {page}.')
        obj = self._get_qt_obj(tile, 'stackedwidget', dac, DQ, kind='dac')
        obj.setCurrentIndex(page)

    # -------------------------------------------------------------------
    # Signal functions
    # -------------------------------------------------------------------
    # function for ADC enabled checkbox
    def ADCEnabled_Toggled(self, tile, adc, DQ='DT'):
        status = self.get_dt_adc_status(tile, adc, DQ)
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Tile{tile}.ADC{adc} ({DQ}) status is {status}.')
        self.logger.info('-------------------------------------------------')
        self.set_dt_adc_status(tile, adc, status, DQ)

    # get the adc clk out list
    def _cal_adc_clkout(self, samplerate):
        clkout = []
        for i in range(4):
            clkout.append(samplerate/2**(i+3))
        return clkout
    # function for ADC sample rate change

    def ADCSampleRate_ValueChanged(self, tile):
        # sample rate affects clk_out and every enabled slice's req_axis_clk,
        # across both DT (2 slices) and QT (4 slices) architectures.
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Sample Rate changed in Tile: {tile}')
        self.logger.info('-------------------------------------------------')
        samplerate = self.get_adc_sample_rate(tile)
        # change value for clk_out
        clkout = self._cal_adc_clkout(samplerate)
        self.set_adc_clkout_list(tile, clkout)
        req_clk = []
        for DQ, nslice in (('DT', 2), ('QT', 4)):
            for adc in range(nslice):
                decmode = self.get_dt_adc_dec_mode(tile, adc, DQ)
                spc = self.get_dt_adc_samples_per_cycle(tile, adc, DQ)
                tmp = samplerate/decmode/spc
                req_clk.append(tmp)
                self.set_dt_adc_req_axis_clk(tile, adc, tmp, DQ)
        # check if every enabled slice's required axis clock still agrees
        if len(set(req_clk)) <= 1:
            self.set_adc_req_axis_clk(tile, req_clk[0] if req_clk else 0)
        else:
            self.set_adc_req_axis_clk(tile, '*Axis Clocking Invalid*')

    # function for ADC digital output value change
    def ADCDigitalOutput_ValueChanged(self, tile, adc, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Digital Output changed in Tile: {tile}, ADC: {adc} ({DQ})')
        self.logger.info('-------------------------------------------------')
        digiout = self.get_dt_adc_digital_output(tile, adc, DQ)
        if digiout == 'Real':
            self.set_dt_adc_stack_page(tile, adc, 0, DQ)
        elif digiout == 'I/Q':
            self.set_dt_adc_stack_page(tile, adc, 1, DQ)
            mixertype = self.get_dt_adc_mixer_type(tile, adc, DQ)
            if mixertype == 'Coarse':
                self.set_dt_adc_stack_page(tile, adc, 2, DQ)

    # function for ADC DEC mode and samples per AXI4-Stream Cycle value change
    def ADCDecModeSamplesPerAXIS_ValueChanged(self, tile, adc, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Dec Mode or Samples Per AXI-Stream changed in Tile: {tile}, ADC: {adc} ({DQ})')
        self.logger.info('-------------------------------------------------')
        samplerate = self.get_adc_sample_rate(tile)
        decmode = self.get_dt_adc_dec_mode(tile, adc, DQ)
        spc = self.get_dt_adc_samples_per_cycle(tile, adc, DQ)
        req_clk = samplerate/decmode/spc
        self.set_dt_adc_req_axis_clk(tile, adc, req_clk, DQ)
        req_axis_clk = []
        for DQ2, nslice in (('DT', 2), ('QT', 4)):
            for a in range(nslice):
                req_axis_clk.append(self.get_dt_adc_req_axis_clk(tile, a, DQ2))
        if len(set(req_axis_clk)) <= 1:
            self.set_adc_req_axis_clk(tile, req_axis_clk[0] if req_axis_clk else 0)
        else:
            self.set_adc_req_axis_clk(tile, '*Axis Clocking Invalid*')

    # function for ADC Mixer type
    def ADCMixerType_ValueChanged(self, tile, adc, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Mixer Type changed in Tile: {tile}, ADC: {adc} ({DQ})')
        self.logger.info('-------------------------------------------------')
        mixermode = self.get_dt_adc_mixer_type(tile, adc, DQ)
        if mixermode == 'Fine':
            self.set_dt_adc_stack_page(tile, adc, 1, DQ)
        elif mixermode == 'Coarse':
            self.set_dt_adc_stack_page(tile, adc, 2, DQ)

    # -------------------------------------------------------------------
    # DAC signal functions -- mirrors the ADC ones above.
    # -------------------------------------------------------------------
    def DACEnabled_Toggled(self, tile, dac, DQ='DT'):
        status = self.get_dt_dac_status(tile, dac, DQ)
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Tile{tile}.DAC{dac} ({DQ}) status is {status}.')
        self.logger.info('-------------------------------------------------')
        self.set_dt_dac_status(tile, dac, status, DQ)

    def DACSampleRate_ValueChanged(self, tile):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'DAC Sample Rate changed in Tile: {tile}')
        self.logger.info('-------------------------------------------------')
        samplerate = self.get_adc_sample_rate(tile)
        clkout = self._cal_adc_clkout(samplerate)
        self.set_adc_clkout_list(tile, clkout)
        req_clk = []
        for DQ, nslice in (('DT', 2), ('QT', 4)):
            for dac in range(nslice):
                intermode = self.get_dt_dac_inter_mode_text(tile, dac, DQ)
                spc = self.get_dt_dac_samples_per_cycle(tile, dac, DQ)
                tmp = samplerate/int(intermode)/spc
                req_clk.append(tmp)
                self.set_dt_dac_req_axis_clk(tile, dac, tmp, DQ)
        if len(set(req_clk)) <= 1:
            self.set_adc_req_axis_clk(tile, req_clk[0] if req_clk else 0)
        else:
            self.set_adc_req_axis_clk(tile, '*Axis Clocking Invalid*')

    def DACAnalogOutput_ValueChanged(self, tile, dac, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'DAC Analog Output changed in Tile: {tile}, DAC: {dac} ({DQ})')
        self.logger.info('-------------------------------------------------')
        analogout = self.get_dt_dac_analog_output(tile, dac, DQ)
        if analogout == 'Real':
            self.set_dt_dac_stack_page(tile, dac, 0, DQ)
        elif analogout == 'I/Q':
            self.set_dt_dac_stack_page(tile, dac, 1, DQ)
            mixertype = self.get_dt_dac_mixer_type(tile, dac, DQ)
            if mixertype == 'Coarse':
                self.set_dt_dac_stack_page(tile, dac, 2, DQ)

    def DACInterModeSamplesPerAXIS_ValueChanged(self, tile, dac, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'DAC Inter Mode or Samples Per AXI-Stream changed in Tile: {tile}, DAC: {dac} ({DQ})')
        self.logger.info('-------------------------------------------------')
        samplerate = self.get_adc_sample_rate(tile)
        intermode = self.get_dt_dac_inter_mode_text(tile, dac, DQ)
        spc = self.get_dt_dac_samples_per_cycle(tile, dac, DQ)
        req_clk = samplerate/int(intermode)/spc
        self.set_dt_dac_req_axis_clk(tile, dac, req_clk, DQ)
        req_axis_clk = []
        for DQ2, nslice in (('DT', 2), ('QT', 4)):
            for d in range(nslice):
                req_axis_clk.append(self.get_dt_dac_req_axis_clk(tile, d, DQ2))
        if len(set(req_axis_clk)) <= 1:
            self.set_adc_req_axis_clk(tile, req_axis_clk[0] if req_axis_clk else 0)
        else:
            self.set_adc_req_axis_clk(tile, '*Axis Clocking Invalid*')

    def DACMixerType_ValueChanged(self, tile, dac, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'DAC Mixer Type changed in Tile: {tile}, DAC: {dac} ({DQ})')
        self.logger.info('-------------------------------------------------')
        mixermode = self.get_dt_dac_mixer_type(tile, dac, DQ)
        if mixermode == 'Fine':
            self.set_dt_dac_stack_page(tile, dac, 1, DQ)
        elif mixermode == 'Coarse':
            self.set_dt_dac_stack_page(tile, dac, 2, DQ)

    # function for button OK
    def ButtonOK_clicked(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info('Button OK clicked, collecting info...')
        self.logger.info('-------------------------------------------------')
        # TODO: collect info for all of the objs
        self.collect_config()
        self.winobj.close()

    # function for buttion Cancel
    def ButtonCancel_clicked(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info('Button Cancel clicked, closing the windows...')
        self.logger.info('-------------------------------------------------')
        self.winobj.close()
    
    # function for collecting config info
    def collect_config(self):
        try:
            with open(self.target_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
            config['parameters'] = {}
            config['parameters']['name'] = ''
            config['parameters']['fullpath'] = ''
            config['parameters']['tag'] = 'xps:rfdc'
        # "name" is deliberately not read from any widget here -- rfdc has
        # no editable Block name field (per direct user request), so
        # whatever value is already in the target file (the JSON
        # template's own default, seeded once by gen_bconfig) is left
        # untouched rather than overwritten.
        for tile in ADC_TILES:
            # Txxx_enable is a very special one, as the name rule is different
            config['parameters'][f'Tile{tile}_enable'] = self.get_tile_status(tile)
            for c in ADC_TILE_ALL_CONFIG:
                key = c['key']
                getfunc = c['get']
                config['parameters'][f't{tile}_{key}'] = str(getattr(self, getfunc)(tile))
            for adc in range(2):
                for c in ADC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    getfunc = c['get']
                    config['parameters'][f't{tile}_DT_adc{adc}_{key}'] = str(getattr(self, getfunc)(tile, adc))
            for adc in range(4):
                for c in ADC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    getfunc = c['get']
                    config['parameters'][f't{tile}_QT_adc{adc}_{key}'] = str(getattr(self, getfunc)(tile, adc, DQ='QT'))
        for tile in DAC_TILES:
            config['parameters'][f'Tile{tile}_enable'] = self.get_tile_status(tile)
            for c in DAC_TILE_ALL_CONFIG:
                key = c['key']
                getfunc = c['get']
                config['parameters'][f't{tile}_{key}'] = str(getattr(self, getfunc)(tile))
            for dac in range(2):
                for c in DAC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    getfunc = c['get']
                    config['parameters'][f't{tile}_DT_dac{dac}_{key}'] = str(getattr(self, getfunc)(tile, dac))
            for dac in range(4):
                for c in DAC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    getfunc = c['get']
                    config['parameters'][f't{tile}_QT_dac{dac}_{key}'] = str(getattr(self, getfunc)(tile, dac, DQ='QT'))
                # 'datapath_mode' is a real QT-only JSON key with no backing
                # widget anywhere in rfdc_ui.py -- deliberately left
                # untouched (whatever value is already in the file on disk
                # is preserved as-is, since `config` started from json.load).
        with open(self.target_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    # function for loading default config info
    def load_config(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Loading config from {self.target_config}...')
        self.logger.info('-------------------------------------------------')
        with open(self.target_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        parameters = config['parameters']
        # no widget to load "name" into -- see collect_config()'s comment
        for tile in ADC_TILES:
            # set Txxx_enable
            s = parameters[f'Tile{tile}_enable']
            self.set_title_status(tile, s)
            # set txxx_clk_out list
            samplerate = parameters[f't{tile}_sample_rate']
            samplerate = float(samplerate)
            clkout = self._cal_adc_clkout(samplerate)
            self.set_adc_clkout_list(tile, clkout)
            for c in ADC_TILE_ALL_CONFIG:
                key = c['key']
                setfunc = c['set']
                s = parameters[f't{tile}_{key}']
                getattr(self, setfunc)(tile, s)
            for adc in range(2):
                for c in ADC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    setfunc = c['set']
                    s = parameters[f't{tile}_DT_adc{adc}_{key}']
                    getattr(self, setfunc)(tile, adc, s)
            for adc in range(4):
                for c in ADC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    setfunc = c['set']
                    s = parameters[f't{tile}_QT_adc{adc}_{key}']
                    getattr(self, setfunc)(tile, adc, s, DQ='QT')
        for tile in DAC_TILES:
            s = parameters[f'Tile{tile}_enable']
            self.set_title_status(tile, s)
            samplerate = parameters[f't{tile}_sample_rate']
            samplerate = float(samplerate)
            clkout = self._cal_adc_clkout(samplerate)
            self.set_adc_clkout_list(tile, clkout)
            for c in DAC_TILE_ALL_CONFIG:
                key = c['key']
                setfunc = c['set']
                s = parameters[f't{tile}_{key}']
                getattr(self, setfunc)(tile, s)
            for dac in range(2):
                for c in DAC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    setfunc = c['set']
                    s = parameters[f't{tile}_DT_dac{dac}_{key}']
                    getattr(self, setfunc)(tile, dac, s)
            for dac in range(4):
                for c in DAC_TILE_SEPARATE_CONFIG:
                    key = c['key']
                    setfunc = c['set']
                    s = parameters[f't{tile}_QT_dac{dac}_{key}']
                    getattr(self, setfunc)(tile, dac, s, DQ='QT')
                # 'datapath_mode' has no backing widget -- see collect_config.
        # set the stack page
        for tile in ADC_TILES:
            for adc in range(2):
                digiout = parameters[f't{tile}_DT_adc{adc}_digital_output']
                mixertype = parameters[f't{tile}_DT_adc{adc}_mixer_type']
                if digiout == 'Real':
                    self.set_dt_adc_stack_page(tile, adc, 0)
                elif mixertype == 'Fine':
                    self.set_dt_adc_stack_page(tile, adc, 1)
                elif mixertype == 'Coarse':
                    self.set_dt_adc_stack_page(tile, adc, 2)
                else:
                    self.logger.error(f'Unknow Mixer Type({mixertype}).')
            for adc in range(4):
                digiout = parameters[f't{tile}_QT_adc{adc}_digital_output']
                mixertype = parameters[f't{tile}_QT_adc{adc}_mixer_type']
                if digiout == 'Real':
                    self.set_dt_adc_stack_page(tile, adc, 0, DQ='QT')
                elif mixertype == 'Fine':
                    self.set_dt_adc_stack_page(tile, adc, 1, DQ='QT')
                elif mixertype == 'Coarse':
                    self.set_dt_adc_stack_page(tile, adc, 2, DQ='QT')
                else:
                    self.logger.error(f'Unknow Mixer Type({mixertype}).')
        for tile in DAC_TILES:
            for dac in range(2):
                analogout = parameters[f't{tile}_DT_dac{dac}_analog_output']
                mixertype = parameters[f't{tile}_DT_dac{dac}_mixer_type']
                if analogout == 'Real':
                    self.set_dt_dac_stack_page(tile, dac, 0)
                elif mixertype == 'Fine':
                    self.set_dt_dac_stack_page(tile, dac, 1)
                elif mixertype == 'Coarse':
                    self.set_dt_dac_stack_page(tile, dac, 2)
                else:
                    self.logger.error(f'Unknow Mixer Type({mixertype}).')
            for dac in range(4):
                analogout = parameters[f't{tile}_QT_dac{dac}_analog_output']
                mixertype = parameters[f't{tile}_QT_dac{dac}_mixer_type']
                if analogout == 'Real':
                    self.set_dt_dac_stack_page(tile, dac, 0, DQ='QT')
                elif mixertype == 'Fine':
                    self.set_dt_dac_stack_page(tile, dac, 1, DQ='QT')
                elif mixertype == 'Coarse':
                    self.set_dt_dac_stack_page(tile, dac, 2, DQ='QT')
                else:
                    self.logger.error(f'Unknow Mixer Type({mixertype}).')

    # -------------------------------------------------------------------
    # Setup Signal functions
    # -------------------------------------------------------------------
    def _safe_connect(self, tile, name, adc, DQ, signal_name, slot, kind='adc'):
        """
        Connect `slot` to the named Qt signal on the widget
        t{tile}_{DQ}_{kind}{adc}_{name}, but skip silently (logging at
        debug level) instead of raising if that widget doesn't exist.
        A handful of tile/slice/page combinations have no backing widget
        anywhere in rfdc_ui.py at all (confirmed gaps, not something this
        mask.py can fix without editing that generated file) -- e.g.
        t225_QT_adc3_enable_iq_coarse. Every getter/setter's *sync-target*
        loop already tolerates this the same way; setup_signal_functions
        runs unconditionally for every tile/slice at dialog startup
        though, so without this same guard here the dialog crashes on
        open the moment it reaches one of those gaps, regardless of
        whether the user ever touches that specific tile -- confirmed by
        direct user report (AttributeError on
        't225_QT_adc3_enable_iq_coarse' inside setup_signal_functions).
        """
        try:
            obj = self._get_qt_obj(tile, name, adc, DQ, kind=kind)
        except AttributeError:
            self.logger.debug(
                f'Tile{tile} slice widget t{tile}_{DQ}_{kind}{adc}_{name} is missing '
                f'(known rfdc_ui.py gap) -- skipping signal wiring.'
            )
            return
        getattr(obj, signal_name).connect(slot)

    def setup_signal_functions(self):
        """
        Docstring for setup_signal_functions:
            Set up signal functions for all of the operations.
        """
        # set up signal functions for ADC tiles
        # set up signal function for sampling rate
        for t in ADC_TILES:
            obj = self._get_qt_obj(t, 'sample_rate')
            obj.editingFinished.connect(lambda tile=t: self.ADCSampleRate_ValueChanged(tile))
        # set up signal function for adc status/digital output/dec mode/
        # samples per cycle/mixer type, across both DT (2 slices) and QT
        # (4 slices) architectures.
        for DQ, nslice in (('DT', 2), ('QT', 4)):
            for t in ADC_TILES:
                for adc in range(nslice):
                    self._safe_connect(t, 'enable_real', adc, DQ, 'toggled', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCEnabled_Toggled(tile, adc, DQ))
                    self._safe_connect(t, 'enable_iq', adc, DQ, 'toggled', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCEnabled_Toggled(tile, adc, DQ))
                    self._safe_connect(t, 'enable_iq_coarse', adc, DQ, 'toggled', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCEnabled_Toggled(tile, adc, DQ))
            for t in ADC_TILES:
                for adc in range(nslice):
                    self._safe_connect(t, 'digital_output_real', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDigitalOutput_ValueChanged(tile, adc, DQ))
                    self._safe_connect(t, 'digital_output_iq', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDigitalOutput_ValueChanged(tile, adc, DQ))
                    self._safe_connect(t, 'digital_output_iq_coarse', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDigitalOutput_ValueChanged(tile, adc, DQ))
            for t in ADC_TILES:
                for adc in range(nslice):
                    self._safe_connect(t, 'dec_mode_real', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, DQ))
                    self._safe_connect(t, 'dec_mode_iq', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, DQ))
                    self._safe_connect(t, 'dec_mode_iq_coarse', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, DQ))
            for t in ADC_TILES:
                for adc in range(nslice):
                    self._safe_connect(t, 'sample_per_cycle_real', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, DQ))
                    self._safe_connect(t, 'sample_per_cycle_iq', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, DQ))
                    self._safe_connect(t, 'sample_per_cycle_iq_coarse', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, DQ))
            for t in ADC_TILES:
                for adc in range(nslice):
                    self._safe_connect(t, 'mixer_type_iq', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCMixerType_ValueChanged(tile, adc, DQ))
                    self._safe_connect(t, 'mixer_type_iq_coarse', adc, DQ, 'activated', lambda *args, tile=t, adc=adc, DQ=DQ: self.ADCMixerType_ValueChanged(tile, adc, DQ))

        # set up signal functions for DAC tiles (both DT and QT arch)
        for t in DAC_TILES:
            obj = self._get_qt_obj(t, 'sample_rate')
            obj.editingFinished.connect(lambda tile=t: self.DACSampleRate_ValueChanged(tile))
        for DQ, nslice in (('DT', 2), ('QT', 4)):
            for t in DAC_TILES:
                for dac in range(nslice):
                    self._safe_connect(t, 'enable_bypassed', dac, DQ, 'toggled', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACEnabled_Toggled(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'enable_fine', dac, DQ, 'toggled', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACEnabled_Toggled(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'enable_coarse', dac, DQ, 'toggled', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACEnabled_Toggled(tile, dac, DQ), kind='dac')
            for t in DAC_TILES:
                for dac in range(nslice):
                    self._safe_connect(t, 'analog_output_bypassed', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACAnalogOutput_ValueChanged(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'analog_output_fine', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACAnalogOutput_ValueChanged(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'analog_output_coarse', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACAnalogOutput_ValueChanged(tile, dac, DQ), kind='dac')
            for t in DAC_TILES:
                for dac in range(nslice):
                    self._safe_connect(t, 'inter_mode_bypassed', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACInterModeSamplesPerAXIS_ValueChanged(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'inter_mode_fine', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACInterModeSamplesPerAXIS_ValueChanged(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'inter_mode_coarse', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACInterModeSamplesPerAXIS_ValueChanged(tile, dac, DQ), kind='dac')
            for t in DAC_TILES:
                for dac in range(nslice):
                    self._safe_connect(t, 'sample_per_cycle_bypassed', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACInterModeSamplesPerAXIS_ValueChanged(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'sample_per_cycle_fine', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACInterModeSamplesPerAXIS_ValueChanged(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'sample_per_cycle_coarse', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACInterModeSamplesPerAXIS_ValueChanged(tile, dac, DQ), kind='dac')
            for t in DAC_TILES:
                for dac in range(nslice):
                    self._safe_connect(t, 'mixer_type_fine', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACMixerType_ValueChanged(tile, dac, DQ), kind='dac')
                    self._safe_connect(t, 'mixer_type_coarse', dac, DQ, 'activated', lambda *args, tile=t, dac=dac, DQ=DQ: self.DACMixerType_ValueChanged(tile, dac, DQ), kind='dac')

        # set up signal function for button OK
        self.ui.ButtonOK.clicked.connect(self.ButtonOK_clicked)
        # set up signal function for button CANCEL
        self.ui.ButtonCANCEL.clicked.connect(self.ButtonCancel_clicked)


if __name__ == "__main__":
    parser = ArgumentParser(description="Usage for RFDC Mask.")
    parser.add_argument('--template', type=str, dest='template', default=None, help='template config file.')
    parser.add_argument('--target', type=str, dest='target', default='rfdc.json',help='target config file.')
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
    op = RFDCOperations(win, opts.template, opts.target, opts.log, opts.debug)
    win.show()
    sys.exit(app.exec())
