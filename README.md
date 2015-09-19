# oandapybot
============

Simple python bot for trading forex on oanda.com

It can only trade one instrument

Built on top of https://github.com/oanda/oandapy

This is only a sample for your robot with simple
sample strategy. You NEED to implement better logic,
otherwise you WILL loose money.

I have my own strategies that I run this bot with,
you need to implement your own logic in logic/strategy.py.

Currently there is a sample moving average cross over
as an example.

To install:
===========

	If you do not have TA-Lib installed, follow these steps:

	1. Get build essentials

	$ sudo apt-get install build-essential
	$ sudo apt-get install python2.7-dev
	$ sudo apt-get install python-pip

	2. Build TA-Lib

	$ wget http://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz/download?use_mirror=iweb
	$ tar zxfv ta-lib-0.4.0-src.tar.gz
	$ cd ta-lib
	$ ./configure --prefix=/usr
	$ make
	$ sudo make install

	1.3 Install python wrapper

	$ sudo pip install Cython
	$ sudo pip install numpy
	$ sudo pip install TA-Lib

	2. Install the rest of dependencies

	$ pip install requirements.txt


To run:
=======

	1. Modify settings.py with your oanda credentials
	2. python main.py

To backtest:
============

	1. Modify settings.py to point your bot to a datafile
	2. python backtest.py