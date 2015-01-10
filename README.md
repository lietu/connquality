What is this?
=============

This is a tool for monitoring your internet connection. It will allow you to 
log the average latency to any endpoint you choose and any errors that might
occur during that.

You can then use that log to make a pretty graph.

Currently monitoring supports the following protocols:
 * TCP/IP
 
It is rather easy to add more protocols and at least the following are planned:
 * HTTP(S)
 * DNS
 * ICMP
 

Requirements and setting up
===========================

This tool requires you to have Python 2.6, 2.7, 3.2, 3.3 or 3.4 (probably 
anything newer works too) and pip installed.

Setting up:
```
pip install -r requirements.txt
```


How to use it?
==============

To start collecting data, use the bin/monitor.py tool:
```
python bin/monitor.py --help
```



Is it working atm?
==================

Every update to GitHub is tested automatically with [Travis CI](https://travis-ci.org/).

The status should be clearly visible here:

[![Build Status](https://travis-ci.org/lietu/connquality.svg)](https://travis-ci.org/lietu/connquality)


Licensing?
==========

Short answer: New BSD or MIT

Long answer: Read LICENSE.txt
