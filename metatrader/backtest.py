# -*- coding: utf-8 -*-
'''
Created on 2015/01/25

@author: samuraitaiga
'''
from __future__ import absolute_import, division
import os
from metatrader.mt5 import get_mt5
from metatrader.mt5 import DEFAULT_MT5_NAME
from metatrader.report import BacktestReport
from metatrader.report import OptimizationReport

try:
    from builtins import str
except ImportError:
    dependencies = ['future']
    subprocess.call([sys.executable, '-m', 'pip', 'install'] + dependencies)
    subprocess.call([sys.executable, '-m', 'pip', '--upgrade'] + dependencies)
finally:
    from builtins import str


class BackTest(object):
    """
    Attributes:
      ea_name(string): ea name
      param(dict): ea parameter
      account_login(int): backtest account login
      symbol(string): currency symbol. e.g.: USDJPY
      from_date(datetime.datetime): backtest from date
      to_date(datetime.datetime): backtest to date
      deposit(int): backtest deposit
      leverage(int): 1:leverage ratio
      model(int): backtest model
        0: Every tick
        1: Control points
        2: Open prices only
      optimization(bool): optimization flag. optimization is enabled if True
      replace_report(bool): replace report flag. replace report is enabled if True
      visual:
        0: Disabled
        1: Enabled

    """

    def __init__(self, ea_name, param, account_login, symbol, period, from_date, to_date, deposit, deposit_currency, leverage,
                    model = 0, replace_report = True, read_report = True, portable_mode = True, visual = 0):
        self.ea_full_path = ea_name
        self.ea_path, self.ea_name = os.path.split(ea_name)
        self.param = param
        self.account_login = account_login
        self.symbol = symbol
        self.period = period
        self.from_date = from_date
        self.to_date = to_date
        self.deposit = deposit
        self.deposit_currency = deposit_currency
        self.leverage = leverage
        self.model = model
        self.replace_report = replace_report
        self.read_report = read_report
        self.portable_mode = portable_mode
        self.optimization = False
        self.visual = visual

    def _prepare(self, alias=DEFAULT_MT5_NAME):
        """
        Notes:
          create backtest config file and parameter file
        """
        self._create_conf(alias=alias)
        self._create_param(alias=alias)

    def _create_conf(self, alias=DEFAULT_MT5_NAME):
        """
        Notes:
            https://www.metatrader5.com/en/terminal/help/start_advanced/start#configuration_file
            create config file(.ini) which is used parameter of terminal64.exe
            in %APPDATA%\\MetaQuotes\\Terminal\\<UUID>\\Tester for non-portable mode
            in %APPDATA%\\Tester for portable mode

            file contents goes to
                [Common]
                Login=5101264
                ProxyEnable=0
                ProxyType=0
                ProxyAddress=192.168.0.1:3128
                ProxyLogin=10
                ProxyPassword=10
                KeepPrivate=1
                NewsEnable=0
                CertInstall=1

                [Tester]
                ;--- The Expert Advisor is located in platform_data_directory\MQL5\Experts\Examples\MACD\
                Expert=Examples\MACD
                ;--- The Expert Advisor parameters are available in platform_installation_directory\MQL5\Profiles\Tester\
                ExpertParameters=MACD.set
                ;--- The symbol for testing/optimization
                Symbol=EURUSD
                ;--- The timeframe for testing/optimization
                Period=M1
                ;--- Emulated account number
                Login=5101264
                ;--- Initial deposit
                Deposit=10000
                ;--- Deposit Currency
                Currency=USD
                ;--- Leverage for testing
                Leverage=1:100
                ;--- The "All Ticks" mode
                Model=1
                ;--- Execution of trade orders without any delay
                ExecutionMode=0
                ;--- 0: No optimization
                ;--- 1: Slow optimization
                Optimization=0
                ;--- Optimization criterion - Maximum balance value
                OptimizationCriterion=0
                ;--- Dates of beginning and end of the testing range
                FromDate=2018.01.01
                ToDate=2018.01.02
                ;--- Custom mode of forward testing
                ForwardMode=0
                ;--- Start date of forward testing
                ForwardDate=2018.01.01
                ;--- A file with a report will be saved to the folder platform_installation_directory
                Report=MACD
                ;--- If the specified report already exists, it will be overwritten
                ReplaceReport=1
                ;--- Set automatic platform shutdown upon completion of testing/optimization
                ShutdownTerminal=1
                ;--- Enable (1) or Disable (0) the visual test mode. If the parameter is not specified, the current setting is used.
                Visual=1
        """

        mt5 = get_mt5(alias = alias, portable_mode = self.portable_mode)
        #print ('_create_conf, self.portable_mode: %r, mt5.appdata_path: %s' % (self.portable_mode, mt5.appdata_path))
        conf_file = os.path.join(mt5.appdata_path, 'Tester', '%s.ini' % self.ea_name)

        # shutdown_terminal must be True.
        # If false, popen don't end and backtest report analyze don't start.
        shutdown_terminal = True

        with open(conf_file, 'w') as fp:
            fp.write('[Common]\n')
            fp.write('Login=%s\n' % str(self.account_login))
            fp.write('ProxyEnable=0\n')
            fp.write('ProxyType=0\n')
            fp.write('ProxyAddress=192.168.0.1:3128\n')
            fp.write('ProxyLogin=10\n')
            fp.write('ProxyPassword=10\n')
            fp.write('KeepPrivate=1\n')
            fp.write('NewsEnable=0\n')
            fp.write('CertInstall=1\n')
            fp.write('\n')
            fp.write('[Tester]\n')
            fp.write(';--- The Expert Advisor is located in platform_data_directory\MQL5\Experts\n')
            fp.write('Expert=%s\n' % self.ea_full_path)
            fp.write(';--- The Expert Advisor parameters are available in platform_installation_directory\MQL5\Profiles\Tester\\n')
            fp.write('ExpertParameters=%s.set\n' % self.ea_name)
            fp.write(';--- The symbol for testing/optimization\n')
            fp.write('Symbol=%s\n' % self.symbol)
            fp.write(';--- The timeframe for testing/optimization\n')
            fp.write('Period=%s\n' % self.period)
            fp.write(';--- Emulated account number\n')
            fp.write('Login=%s\n' % str(self.account_login))
            fp.write(';--- Initial deposit\n')
            fp.write('Deposit=%s\n' % str(self.deposit))
            fp.write(';--- Deposit Currency\n')
            fp.write('Currency=%s\n' % str(self.deposit_currency))
            fp.write(';--- Leverage for testing\n')
            fp.write('Leverage=1:%s\n' % str(self.leverage))
            fp.write(';--- 0 = The "All Ticks" mode\n')
            fp.write('Model=%s\n' % self.model)
            fp.write(';--- 0 = Execution of trade orders without any delay\n')
            fp.write('ExecutionMode=0\n')
            fp.write(';--- 0: No optimization\n')
            fp.write(';--- 1: Slow optimization\n')
            int_optimization = 0
            if self.optimization == True:
                int_optimization = 1
            fp.write('Optimization=%d\n' % int_optimization)
            fp.write(';--- Optimization criterion - Maximum balance value\n')
            fp.write('OptimizationCriterion=0\n')
            fp.write(';--- Dates of beginning and end of the testing range\n')
            fp.write('FromDate=%s\n' % self.from_date.strftime('%Y.%m.%d'))
            fp.write('ToDate=%s\n' % self.to_date.strftime('%Y.%m.%d'))
            fp.write(';--- 0 = No forward testing\n')
            fp.write('ForwardMode=0\n')
            fp.write(';--- Start date of forward testing\n')
            fp.write('ForwardDate=%s\n' % self.to_date.strftime('%Y.%m.%d'))
            fp.write(';--- A file with a report will be saved to the folder platform_installation_directory\n')
            fp.write('Report=%s\n' % self.ea_name)
            fp.write(';--- If the specified report already exists, it will be overwritten\n')
            fp.write('ReplaceReport=%s\n' % str(self.replace_report).lower())
            fp.write(';--- Set automatic platform shutdown upon completion of testing/optimization\n')
            fp.write('ShutdownTerminal=%s\n' % str(shutdown_terminal).lower())
            fp.write(';;--- Enable (1) or Disable (0) the visual test mode. If the parameter is not specified, the current setting is used.\n')
            fp.write('Visual=%s\n' % self.visual)

    def _create_param(self, alias=DEFAULT_MT5_NAME):
        """
        Notes:
            For non-portable mode:
                Create ea parameter file(.set) in %APPDATA%\\MetaQuotes\\Terminal\\<UUID>\\MQL5\\Profiles\\Tester
            For non-portable mode:
                Create ea parameter file(.set) in %APPDATA%\\MQL5\\Profiles\\Tester
        Args:
          ea_name(string): ea name
        """
        mt5 = get_mt5(alias = alias, portable_mode = self.portable_mode)
        #print ('_create_param, self.portable_mode: %r, mt5.appdata_path: %s' % (self.portable_mode, mt5.appdata_path))
        param_file = os.path.join(mt5.appdata_path, 'MQL5', 'Profiles', 'Tester', '%s.set' % self.ea_name)

        with open(param_file, 'w') as fp:
            for k in self.param:
                values = self.param[k].copy()
                data_type = values.pop('type')
                value = values.pop('value')

                # Populate value based on data type
                if data_type == 'bool':
                    if bool(value) == False:
                        fp.write('%s=false||' % (k))
                    else:
                        fp.write('%s=true||' % (k))
                elif data_type == 'int':
                    fp.write('%s=%s||' % (k, value))
                else:
                    raise ('Unexpected data type of %s!' % (data_type))

                if self.optimization:
                    if values.has_key('max') and values.has_key('interval'):
                        interval = values.pop('interval')
                        maximum = values.pop('max')
                        fp.write('%s||%s||%s||Y\n' % (value, interval, maximum))
                    else:
                        # if this value won't be optimized, write unused dummy data for same format.
                        if data_type == 'bool':
                            fp.write('false||0||true||N\n')
                        else:
                            fp.write('0||0||0||N\n')
                else:
                    if type(value) == str:
                        # this ea arg is string, skip items
                        pass
                    else:
                        # write unused dummy data for same format.
                        if data_type == 'bool':
                            fp.write('false||0||true||N\n')
                        else:
                            fp.write('0||0||0||N\n')

    def _get_ini_abs_path(self, alias=DEFAULT_MT5_NAME, portable_mode = False):
        mt5 = get_mt5(alias = alias, portable_mode = portable_mode)
        #print ('_get_ini_abs_path, portable_mode: %r, mt5.appdata_path: %s' % (portable_mode, mt5.appdata_path))
        conf_file = os.path.join(mt5.appdata_path, 'Tester', '%s.ini' % self.ea_name)
        return conf_file

    def run(self, alias=DEFAULT_MT5_NAME):
        """
        Notes:
          run backtest
        """
        self.optimization = False
        ret = None

        self._prepare(alias=alias)
        bt_ini = self._get_ini_abs_path(alias = alias, portable_mode = self.portable_mode)

        mt5 = get_mt5(alias = alias, portable_mode = self.portable_mode)
        #print ('run, self.portable_mode: %r, mt5.appdata_path: %s, bt_ini: %s' % (self.portable_mode, mt5.appdata_path, bt_ini))
        mt5.run(self.ea_name, conf=bt_ini, portable_mode = self.portable_mode)

        if self.read_report == True:
            ret = BacktestReport(self)
        return ret

    def optimize(self, alias=DEFAULT_MT5_NAME):
        """
        """
        self.optimization = True
        ret = None
        self._prepare(alias=alias)
        bt_ini = self._get_ini_abs_path(alias = alias, portable_mode = self.portable_mode)

        mt5 = get_mt5(alias = alias, portable_mode = self.portable_mode)
        #print ('optimize, self.portable_mode: %r, mt5.appdata_path: %s, bt_ini: %s' % (self.portable_mode, mt5.appdata_path, bt_ini))
        mt5.run(self.ea_name, conf=bt_ini, portable_mode = self.portable_mode)

        if self.read_report == True:
            ret = OptimizationReport(self)
        return ret


def load_from_file(dsl_file):
    pass
