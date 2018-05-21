****************************************
py-metatrader
****************************************

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/samuraitaiga/py-metatrader
   :target: https://gitter.im/samuraitaiga/py-metatrader

py-metatrader 0.0.2

Released: 21-May-2018

=============
Introduction
=============

py-metatrader is a python package that provides interfaces to MetaTrader5 (MT5).
`metatrader5`_  is a trading platform that can automate trading (fx, stock, etc...) by your own program (Expert Advisor in MT5).

You can automate simulation (Backtest in MT5), CI, EA development, Deep Learning, AI, Neural Network etc. using this library.

Currently works with Python 2.7 and Python 3.x

Contributing and porting is welcome.


=============
Feature
=============

At the moment, py-metatrader supports:

* Backtest
* Optimization

The goal of py-metatrader is to support execute all features of MetaTrader5 from this library.


============
Installation
============

Install from source:

.. code-block:: bash

    $ git clone https://github.com/viper7882/py-metatrader.git
    $ cd py-metatrader
    $ python setup.py install


============
ChangeLogs
============
* 0.0.2

  * Dropped MT4 support and switched to MT5 support instead.

* 0.0.1

  * first release. backtest and optimization from python.
  * With multiple bug fixes from a few people as well Python3 compatibility


============
Usage
============


Backtest:

.. code-block:: python

    from datetime import datetime
    from metatrader.mt5 import initizalize
    from metatrader.backtest import BackTest
    
    # point mt5 install folder
    initizalize('C:\\Program Files\\FXCM MetaTrader 5')

    # specify backtest period by datetime format
    from_date = datetime(2018, 8, 3)
    to_date = datetime(2018, 8, 5)

    ea_name = 'Moving Average'

    # create ea param by dict.
    param = {
             'Lots': {'value': 0.1},
             'MaximumRisk': {'value': 0.02},
             'DecreaseFactor': {'value': 3.0},
             'MovingPeriod': {'value': 12},
             'MovingShift': {'value': 6}
             }
    # create backtest object with specified spread
    backtest = BackTest(ea_name, param, 'USDJPY', 'M5', from_date, to_date, spread=10)

    # run backtest
    ret = backtest.run()

    # you can get result from result object
    # for example you can print gross profit
    print ret.gross_profit

    # and print net profit
    print ret.profit

.. _metatrader5: https://www.metatrader5.com/
.. _pip: https://pip.pypa.io/en/stable/
