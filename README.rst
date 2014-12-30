StorjTorrent
============

|Build Status| |Coverage Status|

StorjTorrent is a wrapper library for libtorrent’s Python bindings. It
allows Storj packages to create torrents, seed files to other Storj
nodes, and retrieve files using their hashes.

Building
========

You will need to ensure `Boost`_ is properly installed so you can
properly build and install ``libtorrent``:

::

    $ wget http://sourceforge.net/projects/boost/files/boost/1.57.0/boost_1_57_0.tar.gz
    $ tar -zxvf boost_*.tar.gz
    $ cd boost_*
    $ ./bootstrap.sh
    $ ./b2
    $ sudo ./b2 install

After Boost is successfully built, you can build and install
``libtorrent``:

::

    $ wget http://downloads.sourceforge.net/project/libtorrent/libtorrent/libtorrent-rasterbar-1.0.3.tar.gz
    $ tar -zxvf libtorrent-*.tar.gz
    $ cd libtorrent-rasterbar-1.0.3
    $ ./configure --enable-python-binding
    $ make
    $ sudo make install

You may also need to run:

::

    $ cd bindings/python
    $ sudo python setup.py install

OSX
---

You may need to have XCode’s command line tools installed if you don’t
already have them set up:

::

    $ xcode-select --install

If you are using OSX, you can use the `Homebrew`_ system to install
Boost (with Python support) and libtorrent:

::

    $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    $ brew install boost-python 
    $ brew install libtorrent-rasterbar --with-python

Installing Inside a Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your virtual environment is using Brew’s python:

::

    $ mkvirtualenv -p /usr/local/bin/python storjtorrent

If you are installing inside a virtual environment, you can try the
following (after you install boost-python with homebrew):

::

    $ brew install boost --with-python
    $ brew install boost-build
    $ wget http://downloads.sourceforge.net/project/libtorrent/libtorrent/libtorrent-rasterbar-1.0.3.tar.gz
    $ tar -zxvf libtorrent-*.tar.gz
    $ cd libtorrent-rasterbar-1.0.3
    $ ./configure --disable-debug --disable-dependency-tracking --disable-silent-rules --enable-encryption --prefix=$VIRTUAL_ENV --with-boost=/usr/local/opt/boost --enable-python-binding --with-libiconv --with-boost-python=boost_python-mt PYTHON=python PYTHON_LDFLAGS="$(python-config --libs)"
    $ make
    $ make install

Ubuntu
------

Install supporting tools and libraries:

::

    $ apt-get install build-essential libboost-all-dev
    $ apt-get source python-libtorrent
    $ apt-get build-dep python-libtorrent

Create a new virtual environment. For example, if you have
``virtualenvwrapper`` installed, you can use the following to create and
enter a new virtual environment called ``storjtorrent``:

::

    $ mkvirtualenv storjtorrent

Then, once inside the virtual environment, run the following commands:

::

    $ wget http://down

.. _Boost: http://www.boost.org/
.. _Homebrew: http://brew.sh/

.. |Build Status| image:: https://travis-ci.org/Storj/storjtorrent.svg
   :target: https://travis-ci.org/Storj/storjtorrent
.. |Coverage Status| image:: https://img.shields.io/coveralls/Storj/storjtorrent.svg
   :target: https://coveralls.io/r/Storj/storjtorrent