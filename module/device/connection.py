import os
import subprocess

import requests
import uiautomator2 as u2

from module.config.config import AzurLaneConfig
from module.logger import logger


class Connection:
    _adb_binary = ''
    adb_binary_list = [
        r'.\adb\adb.exe',
        r'.\python-3.7.6.amd64\Lib\site-packages\adbutils\binaries\adb.exe',
        r'.\python\Lib\site-packages\adbutils\binaries\adb.exe',
    ]

    def __init__(self, config):
        """
        Args:
            config(AzurLaneConfig):
        """
        logger.hr('Device')
        self.config = config
        self.serial = str(self.config.SERIAL)
        self.device = self.connect(self.serial)
        self.disable_uiautomator2_auto_quit()
        # if self.config.DEVICE_SCREENSHOT_METHOD == 'aScreenCap':
        #     self._ascreencap_init()

    @property
    def adb_binary(self):
        if self._adb_binary:
            return self._adb_binary

        # Try existing adb.exe
        for file in self.adb_binary_list:
            if os.path.exists(file):
                logger.attr('Adb_binary', file)
                self._adb_binary = file
                return file

        # Use adb.exe in system PATH
        file = 'adb.exe'
        logger.attr('Adb_binary', file)
        self._adb_binary = file
        return file

    def adb_command(self, cmd, serial=None):
        if serial:
            cmd = [self.adb_binary, '-s', serial] + cmd
        else:
            cmd = [self.adb_binary] + cmd

        # Use shell=True to disable console window when using GUI.
        # Although, there's still a window when you stop running in GUI, which cause by gooey.
        # To disable it, edit gooey/gui/util/taskkill.py
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        return process.communicate(timeout=10)[0]

    def adb_shell(self, cmd, serial=None):
        cmd.insert(0, 'shell')
        return self.adb_command(cmd, serial)

    def adb_exec_out(self, cmd, serial=None):
        cmd.insert(0, 'exec-out')
        return self.adb_command(cmd, serial)

    def _adb_connect(self, serial):
        if serial.startswith('127.0.0.1'):
            msg = self.adb_command(['connect', serial]).decode("utf-8")
            if msg.startswith('unable'):
                logger.error('Unable to connect %s' % serial)
                exit(1)
            else:
                logger.info(msg.strip())

    def connect(self, serial):
        """Connect to a device.

        Args:
            serial (str): device serial or device address.

        Returns:
            uiautomator2.UIAutomatorServer: Device.
        """
        self._adb_connect(serial)
        device = u2.connect(serial)
        return device

    def disable_uiautomator2_auto_quit(self, port=7912, expire=300000):
        self.adb_command(['forward', 'tcp:%s' % port, 'tcp:%s' % port], serial=self.serial)
        requests.post('http://127.0.0.1:%s/newCommandTimeout' % port, data=str(expire))

    def _ascreencap_init(self):
        logger.hr('aScreenCap init')

        arc = self.adb_exec_out(['getprop', 'ro.product.cpu.abi'], serial=self.serial).decode('utf-8').strip()
        sdk = self.adb_exec_out(['getprop', 'ro.build.version.sdk'], serial=self.serial).decode('utf-8').strip()
        logger.info(f'cpu_arc: {arc}, sdk_ver: {sdk}')

        if int(sdk) not in range(21, 26) or not os.path.exists(f'./ascreencap/{arc}'):
            logger.warning('No suitable version of aScreenCap lib is available')
            logger.info('Please use ADB or uiautomator2 screenshot instead')
            exit(1)

        filepath = f'./ascreencap/{arc}/ascreencap'
        logger.info(f'pushing {filepath}')
        self.adb_command(['push', filepath, self.config.ASCREENCAP_FILEPATH], serial=self.serial)

        logger.info(f'chmod 0777 {self.config.ASCREENCAP_FILEPATH}')
        self.adb_shell(['chmod', '0777', self.config.ASCREENCAP_FILEPATH], serial=self.serial)
