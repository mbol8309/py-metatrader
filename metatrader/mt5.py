# -*- coding: utf-8 -*-
"""
@author: samuraitaiga
"""
import os
import sys
import logging
import subprocess

try:
    import winreg
except:
    import _winreg as winreg
import codecs

_mt5s = {}
_portable_mode = False

DEFAULT_MT5_NAME = 'default'
# mt5 program file path is written in origin.txt
ORIGIN_TXT = 'origin.txt'
MT5_EXE = 'terminal64.exe'


class MT5(object):
    """
    Notes:
      meta trader 5 class which can launch metatrader5.
      this class will only launch metatrader5,
      because metatrader5 can launch either normal mode or backtest mode.
    """
    prog_path = None
    appdata_path = None

    def __init__(self, prog_path):
        self.prog_path_raw = prog_path
        self.get_appdata_path

    @property
    def get_appdata_path(self):
        global _portable_mode
        if os.path.exists(self.prog_path_raw):
            self.prog_path = self.prog_path_raw
            if ((is_uac_enabled() == True) and (_portable_mode == False)):
                try:
                    self.appdata_path = get_appdata_path(self.prog_path_raw)
                except IOError as e:
                    _portable_mode = True
                    self.appdata_path = self.prog_path_raw
            else:
                self.appdata_path = self.prog_path_raw

        else:
            err_msg = 'prog_path_raw %s not exists' % self.prog_path_raw
            logging.error(err_msg)
            raise IOError(err_msg)

        if not has_mt5_subdirs(self.appdata_path):
            err_msg = 'appdata path %s has not sufficient dirs' % self.appdata_path
            logging.error(err_msg)
            raise IOError(err_msg)

    def run(self, ea_name, conf=None, portable_mode=False):
        """
        Notes:
          run terminal.exe.
        Args:
          conf(string): abs path of conf file.
            details see mt5 help doc Client Terminal/Tools/Configuration at Startup
        """
        import subprocess

        if conf:
            prog_raw = '%s' % os.path.join(self.prog_path, MT5_EXE)

            if not os.path.exists(self.prog_path) and not os.path.isfile(prog_raw):
                err_msg = 'MT5 path, %s does not exist!!!' % (prog_raw)
                logging.error(err_msg)
                raise IOError(err_msg)

            if portable_mode == True:
                prog = '"%s" /portable' % prog_raw
            else:
                prog = '"%s"' % prog_raw

            if not os.path.isfile(conf):
                err_msg = 'conf path, \"%s\" does not exist!!!' % (conf)
                logging.error(err_msg)
                raise IOError(err_msg)

            conf = '/config:"%s"' % conf
            cmd = '%s %s' % (prog, conf)

            #print ('Calling subprocess with cmd: %s' % (cmd))
            p = subprocess.Popen(cmd)
            p.wait()
            if ((p.returncode == 0) or (p.returncode == 3)):
                # Logging info will cause command prompt to wait for enter key which is not required in this case
                #logging.info('cmd[%s] succeeded', cmd)
                pass
            else:
                err_msg = 'run mt5 with cmd[%s] failed with %d error code!!' % (cmd, p.returncode)
                logging.error(err_msg)
                raise RuntimeError(err_msg)


def has_mt5_subdirs(appdata_path):
    """
    Note:
      check this appdata path has required mt5 sub dirs.
      currently chech backtest related dirs.
      - Profiles
      - Tester
      - MQL5\\Experts
      - MQL5\\Libraries
    Returns:
      True if has required mt5 sub dirs,
      False if doesn't have
    """
    sub_dirs = [os.path.join(appdata_path, 'Profiles'),
                os.path.join(appdata_path, 'Tester'),
                os.path.join(appdata_path, 'MQL5', 'Experts'),
                os.path.join(appdata_path, 'MQL5', 'Libraries')]
    ret = True

    for sub_dir in sub_dirs:
        if not os.path.exists(sub_dir) and not os.path.isdir(sub_dir):
            ret = False

    return ret


def is_uac_enabled():
    """
    Note:
      check uac is enabled or not from reg value.
    Returns:
     True if uac is enabled, False if uac is disabled.
    """
    import winreg

    reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System', 0, winreg.KEY_READ)
    value, regtype = winreg.QueryValueEx(reg_key, 'EnableLUA')

    if value == 1:
        # reg value 1 means UAC is enabled
        return True
    else:
        return False


def get_appdata_path(program_file_dir):
    """
    Returns:
      AppData path corresponding to provided program file path
      e.g.: C:\\Users\\UserName\\AppData\\Roaming\\MetaQuotes\\Terminal\\7269C010EA668AEAE793BEE37C26ED57
    """
    app_data = os.environ.get('APPDATA')
    mt5_appdata_path = os.path.join(app_data, 'MetaQuotes', 'Terminal')

    app_dir = None

    walk_depth = 1
    for root, dirs, files in os.walk(mt5_appdata_path):
        # search ORIGIN_TXT until walk_depth
        depth = root[len(mt5_appdata_path):].count(os.path.sep)

        if ORIGIN_TXT in files:
            origin_file = os.path.join(root, ORIGIN_TXT)

            import codecs
            with codecs.open(origin_file, 'r', 'utf-16') as fp:
                line = fp.read()
                if line == program_file_dir:
                    app_dir = root
                    break

        if depth >= walk_depth:
            dirs[:] = []

    if app_dir == None:
        err_msg = '%s does not have appdata dir!.' % program_file_dir
        logging.error(err_msg)
        raise IOError(err_msg)

    return app_dir


def initialize(ntpath, portable_mode = False, alias = DEFAULT_MT5_NAME):
    """
    Notes:
      initialize mt5
    Args:
      ntpath(string): mt5 install folder path.
        e.g.: C:\\Program Files (x86)\\MetaTrader 4 - Alpari Japan
      alias(string): mt5 object alias name. default value is DEFAULT_MT5_NAME
    """
    global _mt5s
    global _portable_mode
    _portable_mode = portable_mode
    if alias not in _mt5s:
        # store mt5 object with alias name
        _mt5s[alias] = MT5(ntpath, )
    else:
        logging.info('%s is already initialized' % alias)


def get_mt5(alias = DEFAULT_MT5_NAME, portable_mode = False):
    """
    Notes:
      return mt5 object which is initialized.
    Args:
      alias(string): mt5 object alias name. default value is DEFAULT_MT5_NAME
    Returns:
      mt5 object(metatrader.backtest.MT5): instantiated mt5 object
    """
    global _mt5s
    global _portable_mode
    
    _portable_mode = portable_mode

    if alias in _mt5s:
        _mt5s[alias].get_appdata_path
        return _mt5s[alias]
    else:
        raise RuntimeError('mt5[%s] is not initialized.' % alias)
