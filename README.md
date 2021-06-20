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
 
 
What does the result look like?
===============================

![Screenshot](example.png?raw=true "Screenshot")
 

Windows usage
=============

The binary .exe files are available at [the project releases page](https://github.com/lietu/connquality/releases/).

To start collecting data use the monitor.exe tool:
```
monitor --help
```

To then graph the results use the graph.exe tool:
```
graph --help
```

You can also just double-click on graph.exe to run on defaults, assuming you're
logging to the default file with the monitor as well.


Other platforms
===============

This tool requires you to have Python 2.6, 2.7, 3.2, 3.3 or 3.4 (probably 
anything newer works too) and pip installed.

Setting up:
```
pip install -r requirements.txt
```

To start collecting data, use the monitor.py tool:
```
python monitor.py --help
```

To then graph the results use the graph.py tool:
```
python graph.py --help
```


Example usage
=============

**Monitoring**

The only required parameter is one or more `--tcp=address:port`.

E.g. to monitor that you can access google.com and opendns' guide:
```
python monitor.py --tcp=google.com:80 --tcp=guide.opendns.com:80
```

Or on Windows:
```
monitor --tcp=google.com:80 --tcp=guide.opendns.com:80
```


**Graphing**

And to graph with the default settings:
```
python graph.py
```

Or on Windows
```
graph
```



Is it working atm?
==================

Every update to GitHub is tested automatically with [Travis CI](https://travis-ci.org/).

The status should be clearly visible here:

[![Build Status](https://travis-ci.org/lietu/connquality.svg)](https://travis-ci.org/lietu/connquality)


Building for Windows
====================

If you are planning on updating the Windows release, you need to know how to do it.
This is not required for Windows users using the .exe versions of the tools.

You'll need to download matplotlib and numpy (check requirements.txt for versions) manually.

You also need to install cx_Freeze (`pip install cx_Freeze`) and [pywin32](http://sourceforge.net/projects/pywin32/).

Replace the `C:\python27\` path with whatever your installation directory is.

```
pip install -r requirements.txt
python setup.py build
```

You'll have the windows distribution files available under *build/something*.


Licensing?
==========

Short answer: New BSD or MIT

Long answer: Read [LICENSE.txt](https://github.com/lietu/connquality/blob/master/LICENSE.txt)


# Financial support

This project has been made possible thanks to [Cocreators](https://cocreators.ee) and [Lietu](https://lietu.net). You can help us continue our open source work by supporting us on [Buy me a coffee](https://www.buymeacoffee.com/cocreators).

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cocreators)
