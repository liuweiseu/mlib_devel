import sys
import logging
import json
from argparse import ArgumentParser
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from rfdc_ui import Ui_MainWindow
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import make_rich_logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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
    def __init__(self, winobj, src_config='rfdc.json', dst_config='rfdc.json', logdir='.', debug=False):
        if debug:
            self.logger = make_rich_logger('rfdc.log', logging.DEBUG, mode='a', logdir=logdir)
        else:
            self.logger = make_rich_logger('rfdc.log', logging.ERROR, mode='a', logdir=logdir)
    
        self.logger.info('*************************************************')
        self.logger.info('RFDC Mask started.')
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

    def _get_qt_obj(self, tile, name, adc=None, DQ=None):
        """
        Docstring for _get_qt_obj:
            get the QT object.
        :param tile (uint8) : tile number.
        :param name (str)   : object name.
        :param adc  (uint8) : adc ID - 0 or 1.
        :param DQ   (str)   : Dual Tile(DT) or Quad Tile(QT).
        """
        if tile not in ADC_TILES:
            self.logger.error(f'Tile{tile} is not in {ADC_TILES}')
            raise ValueError(f'Tile{tile} is not in {ADC_TILES}')
        if adc == None:
            return getattr(self.ui, f't{tile}_{name}')
        else:
            return getattr(self.ui, f't{tile}_{DQ}_adc{adc}_{name}')
    
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
        obj.setCurrentText(val)

    def get_dt_adc_status(self, tile, adc):
        """
        Docstring for get_dt_adc_status
        
        :param tile (uint8): tile number
        :param adc. (uin8) : adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        status = obj.isChecked()
        self.logger.debug(f'Tile{tile}.ADC{adc}(Dual Tile) status is {status}.')
        # also set the other status for sync
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setChecked(status)
        return self._convert_status(status)
    
    def set_dt_adc_status(self, tile, adc, status):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setChecked(status)

    def get_dt_adc_digital_output(self, tile, adc):
        """
        Docstring for get_dt_digital_output
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        val = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) digital output is {val}.')
        # also set the other status for sync
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(val)
        return val
    
    def set_dt_adc_digital_output(self, tile, adc, val):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(val)

    def get_dt_adc_dec_mode(self, tile, adc):
        """
        Docstring for get_dt_adc_dec_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        decmode = obj.currentIndex()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) DEC mode is x{ADC_DEC_MODE[decmode]}.')
        # also set the other value for sync
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentIndex(decmode)
        return ADC_DEC_MODE[decmode]

    def get_dt_adc_dec_mode_text(self, tile, adc):
        """
        Docstring for get_dt_adc_dec_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        decmode = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) DEC mode is decmode].')
        # also set the other value for sync
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(decmode)
        return decmode

    def set_dt_adc_dec_mode(self, tile, adc, decmode):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            if isinstance(decmode, int):
                obj.setCurrentIndex(decmode)
            elif isinstance(decmode, str):
                obj.setCurrentText(decmode)
            else:
                self.logger.error(f'decmode({decmode}) is not supported.')
    
    def get_dt_adc_samples_per_cycle(self, tile, adc):
        """
        Docstring for get_dt_adc_samples_per_cycle
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        spc = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) samples per cycle is {spc}.')
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(spc)
        return int(spc)
    
    def set_dt_adc_samples_per_cycle(self, tile, adc, spc):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
        obj.setCurrentText(spc)

    def get_dt_adc_req_axis_clk(self, tile, adc):
        """
        Docstring for get_dt_adc_req_axis_clk
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        value = obj.value()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile)  required axis clock is {value}MHz.')
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setValue(value)
        return value

    def set_dt_adc_req_axis_clk(self, tile, adc, freq):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setValue(float(freq))

    def get_dt_adc_mixer_type(self, tile, adc):
        """
        Docstring for get_dt_adc_mixer_type
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        mixertype = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Mixer Type is {mixertype}.')
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(mixertype)
        return mixertype

    def set_dt_adc_mixer_type(self, tile, adc, mixertype):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(mixertype)

    def get_dt_adc_mixer_mode(self, tile, adc):
        """
        Docstring for get_dt_adc_mixer_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        mixermode = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Mixer Type is {mixermode}.')
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(mixermode)
        return mixermode
    
    def set_dt_adc_mixer_mode(self, tile, adc, mixermode):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(mixermode)
        
    def get_dt_adc_nco_freq(self, tile, adc):
        """
        Docstring for get_dt_adc_nco_freq
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'nco_freq_iq', adc, 'DT')
        ncofreq = obj.value()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) NCO Freq is {ncofreq} GHz.')
        return ncofreq
    
    def set_dt_adc_nco_freq(self, tile, adc, ncofreq):
        """
        Docstring for set_dt_adc_nco_freq
        
        :param tile     (uint8): tile number
        :param adc      (uint8): adc id - 0 or 1.
        :param ncofreq  (float or str): nco frequency in GHz.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} NCO Freqnency to {ncofreq} GHz.')
        obj = self._get_qt_obj(tile, 'nco_freq_iq', adc, 'DT')
        obj.setValue(float(ncofreq))

    def get_dt_adc_nco_phase(self, tile, adc):
        """
        Docstring for get_dt_adc_nco_phase
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'nco_phase_iq', adc, 'DT')
        ncophase = obj.value()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) NCO Phase is {ncophase}.')
        return ncophase

    def set_dt_adc_nco_phase(self, tile, adc, ncophase):
        """
        Docstring for set_dt_adc_nco_phase
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param ncophase (float or str): nco phase.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} NCO Phase to {ncophase}.')
        obj = self._get_qt_obj(tile, 'nco_phase_iq', adc, 'DT')
        obj.setValue(float(ncophase))

    def get_dt_adc_coarse_freq(self, tile, adc):
        """
        Docstring for get_dt_adc_coarse_freq
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'coarse_freq', adc, 'DT')
        freq = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Coarse Freq is {freq}MHz.')
        return freq

    def set_dt_adc_coarse_freq(self, tile, adc, freq):
        """
        Docstring for set_dt_adc_coarse_freq
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param freq (str)  : coarse frequency in ??
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} Coarse Frequency to {freq}.')
        obj = self._get_qt_obj(tile, 'coarse_freq', adc, 'DT')
        obj.setCurrentText(freq)

    def get_dt_adc_nyquist_zone(self, tile, adc):
        """
        Docstring for get_dt_adc_nyquist_zone
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        nzone = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Nyquist Zone is {nzone}.')
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(nzone)
        return nzone

    def set_dt_adc_nyquist_zone(self, tile, adc, nzone):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(nzone)

    def get_dt_adc_cal_mode(self, tile, adc):
        """
        Docstring for get_dt_adc_cal_mode
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        # get current stack page first
        page = self.get_dt_adc_stack_page(tile, adc)
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
        obj = self._get_qt_obj(tile, source, adc, 'DT')
        calmode = obj.currentText()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) Calibration Mode is {calmode}.')
        for t in targets:
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(calmode)
        return calmode

    def set_dt_adc_cal_mode(self, tile, adc, calmode):
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
            obj = self._get_qt_obj(tile, t, adc, 'DT')
            obj.setCurrentText(calmode)
        
    def get_dt_adc_stack_page(self, tile, adc):
        """
        Docstring for get_dt_adc_stack_page
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        """
        obj = self._get_qt_obj(tile, 'stackedwidget', adc, 'DT')
        page = obj.currentIndex()
        self.logger.debug(f'Tile{tile}.ADC{adc} (Dual Tile) stack page is {page}.')
        return page

    def set_dt_adc_stack_page(self, tile, adc, page):
        """
        Docstring for set_dt_adc_stack_page
        
        :param tile (uint8): tile number
        :param adc  (uint8): adc id - 0 or 1.
        :param page (uint8): page id - 0 or 1.
        """
        self.logger.debug(f'Set Tile{tile}.ADC{adc} (Dual Tile) stack page to {page}.')
        obj = self._get_qt_obj(tile, 'stackedwidget', adc, 'DT')
        obj.setCurrentIndex(page)

    # -------------------------------------------------------------------
    # Signal functions
    # -------------------------------------------------------------------
    # function for ADC enabled checkbox
    def ADCEnabled_Toggled(self, tile, adc, DQ='DT'):
        status = self.get_dt_adc_status(tile, adc)
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Tile{tile}.ADC{adc} status is {status}.')
        self.logger.info('-------------------------------------------------')
        self.set_dt_adc_status(tile, adc, status)

    # get the adc clk out list
    def _cal_adc_clkout(self, samplerate):
        clkout = []
        for i in range(4):
            clkout.append(samplerate/2**(i+3))
        return clkout
    # function for ADC sample rate change

    def ADCSampleRate_ValueChanged(self, tile):
        # sample rate affects clk_out and adc0_req_axis_clk_real and adc1_req_axis_clk_real
        # get sample rate val
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Sample Rate changed in Tile: {tile}')
        self.logger.info('-------------------------------------------------')
        samplerate = self.get_adc_sample_rate(tile)
        # change value for clk_out
        clkout = self._cal_adc_clkout(samplerate)
        self.set_adc_clkout_list(tile, clkout)
        # change value for adc0_req_axis_clk_real and adc1_req_axis_clk_real
        # TODO: this only works for Dual tile, so we need to add more code for Quad tile.
        req_clk = []
        for adc in range(2):
            decmode = self.get_dt_adc_dec_mode(tile, adc)
            spc = self.get_dt_adc_samples_per_cycle(tile, adc)
            tmp = samplerate/decmode/spc
            req_clk.append(tmp)
            self.set_dt_adc_req_axis_clk(tile, adc, tmp)
        # check if the two req_clk are the same
        # TODO: this only works for Dual tile, so we need to add more code for Quad tile.
        if req_clk[0] == req_clk[1]:
            self.set_adc_req_axis_clk(tile, req_clk[0])
        else:
            self.set_adc_req_axis_clk(tile, '*Axis Clocking Invalid*')

    # function for ADC digital output value change
    def ADCDigitalOutput_ValueChanged(self, tile, adc, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Digital Output changed in Tile: {tile}, ADC: {adc}')
        self.logger.info('-------------------------------------------------')
        digiout = self.get_dt_adc_digital_output(tile, adc)
        if digiout == 'Real':
            self.set_dt_adc_stack_page(tile, adc, 0)
        elif digiout == 'I/Q':
            self.set_dt_adc_stack_page(tile, adc, 1)
            mixertype = self.get_dt_adc_mixer_type(tile, adc)
            if mixertype == 'Coarse':
                self.set_dt_adc_stack_page(tile, adc, 2)

    # function for ADC DEC mode and samples per AXI4-Stream Cycle value change
    def ADCDecModeSamplesPerAXIS_ValueChanged(self, tile, adc, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Dec Mode or Samples Per AXI-Stream changed in Tile: {tile}, ADC: {adc}')
        self.logger.info('-------------------------------------------------')
        samplerate = self.get_adc_sample_rate(tile)
        decmode = self.get_dt_adc_dec_mode(tile, adc)
        spc = self.get_dt_adc_samples_per_cycle(tile, adc)
        req_clk = samplerate/decmode/spc
        self.set_dt_adc_req_axis_clk(tile, adc, req_clk)
        req_axis_clk = []
        for adc in range(2):
            req_axis_clk.append(self.get_dt_adc_req_axis_clk(tile, adc))
        if req_axis_clk[0] == req_axis_clk[1]:
            self.set_adc_req_axis_clk(tile, req_axis_clk[0])
        else:
            self.set_adc_req_axis_clk(tile, '*Axis Clocking Invalid*')
    
    # function for ADC Mixer type
    def ADCMixerType_ValueChanged(self, tile, adc, DQ='DT'):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'ADC Mixer Type changed in Tile: {tile}, ADC: {adc}')
        self.logger.info('-------------------------------------------------')
        mixermode = self.get_dt_adc_mixer_type(tile, adc)
        if mixermode == 'Fine':
            self.set_dt_adc_stack_page(tile, adc, 1)
        elif mixermode == 'Coarse':
            self.set_dt_adc_stack_page(tile, adc, 2)

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
            with open(self.dst_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
            config['parameters'] = {}
            config['parameters']['name'] = ''
            config['parameters']['fullpath'] = ''
            config['parameters']['tag'] = 'xps:rfdc'
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
        with open(self.dst_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    # function for loading default config info
    def load_config(self):
        self.logger.info('-------------------------------------------------')
        self.logger.info(f'Loading default config from {self.src_config}...')
        self.logger.info('-------------------------------------------------')
        with open(self.src_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        parameters = config['parameters']
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

    # -------------------------------------------------------------------
    # Setup Signal functions
    # -------------------------------------------------------------------
    def setup_signal_functions(self):
        """
        Docstring for setup_signal_functions:
            Set up signal functions for all of the operations. 
        """
        # set up signal functions for ADC titles
        # set up signal function for sampling rate
        for t in ADC_TILES:
            obj = self._get_qt_obj(t, 'sample_rate')
            obj.editingFinished.connect(lambda tile=t: self.ADCSampleRate_ValueChanged(tile))
        # set up signal function for adc status
        for t in ADC_TILES:
            for adc in range(2):
                self._get_qt_obj(t, 'enable_real', adc, 'DT').toggled.connect(lambda *args, tile=t, adc=adc: self.ADCEnabled_Toggled(tile, adc, 'DT'))
                self._get_qt_obj(t, 'enable_iq', adc, 'DT').toggled.connect(lambda *args, tile=t, adc=adc: self.ADCEnabled_Toggled(tile, adc, 'DT'))
                self._get_qt_obj(t, 'enable_iq_coarse', adc, 'DT').toggled.connect(lambda *args, tile=t, adc=adc: self.ADCEnabled_Toggled(tile, adc, 'DT'))
        # set up signal function for digital output
        for t in ADC_TILES:
            for adc in range(2):
                self._get_qt_obj(t, 'digital_output_real', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDigitalOutput_ValueChanged(tile, adc, 'DT'))
                self._get_qt_obj(t, 'digital_output_iq', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDigitalOutput_ValueChanged(tile, adc, 'DT'))
                self._get_qt_obj(t, 'digital_output_iq_coarse', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDigitalOutput_ValueChanged(tile, adc, 'DT'))
        # set up signal function for dec mode
        for t in ADC_TILES:
            for adc in range(2):
                self._get_qt_obj(t, 'dec_mode_real', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, 'DT'))
                self._get_qt_obj(t, 'dec_mode_iq', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, 'DT'))
                self._get_qt_obj(t, 'dec_mode_iq_coarse', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, 'DT'))
        # set up signal function for samples per cycle
        for t in ADC_TILES:
            for adc in range(2):
                self._get_qt_obj(t, 'sample_per_cycle_real', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, 'DT'))
                self._get_qt_obj(t, 'sample_per_cycle_iq', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, 'DT'))
                self._get_qt_obj(t, 'sample_per_cycle_iq_coarse', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCDecModeSamplesPerAXIS_ValueChanged(tile, adc, 'DT'))
        # st up signal function for Mixer type
        for t in ADC_TILES:
            for adc in range(2):
                self._get_qt_obj(t, 'mixer_type_iq', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCMixerType_ValueChanged(tile, adc, 'DT'))
                self._get_qt_obj(t, 'mixer_type_iq_coarse', adc, 'DT').activated.connect(lambda *args, tile=t, adc=adc: self.ADCMixerType_ValueChanged(tile, adc, 'DT'))
        # set up signal functions for DAC tiles
        # TODO: add these signal functions for DAC tiles
        # set up signal function for button OK
        self.ui.ButtonOK.clicked.connect(self.ButtonOK_clicked)
        # set up signal function for button CANCEL
        self.ui.ButtonCANCEL.clicked.connect(self.ButtonCancel_clicked)


if __name__ == "__main__":
    parser = ArgumentParser(description="Usage for RFDC Mask.")
    parser.add_argument('-s','--src', type=str, dest='src', default=None, help='Source config file.')
    parser.add_argument('-d','--dst', type=str, dest='dst', default='rfdc.json',help='Dest config file.')
    parser.add_argument('-l', '--log', type=str, dest='log', default='.', help='The directory for log files.')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true', default=False, help='Turn on verbose.')
    opts = parser.parse_args()

    app = QApplication(sys.argv)
    script_path = os.path.realpath(__file__)
    curdir = os.path.dirname(script_path)
    app.setWindowIcon(QIcon(f"{curdir}/icon/casper_icon.png"))
    win = MainWindow()
    op = RFDCOperations(win, opts.src, opts.dst, opts.log, opts.debug)
    win.show()
    sys.exit(app.exec())
