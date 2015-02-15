StorjTorrent
============

|Build Status| |Coverage Status| |PyPi Version|

StorjTorrent is a wrapper library for libtorrent's Python bindings. It
allows Storj packages to create torrents, seed files to other Storj
nodes, and retrieve files using their hashes.

Building
========

You will need to ensure `Boost <http://www.boost.org/>`__ is properly
installed so you can properly build and install ``libtorrent``:

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

You may need to have XCode's command line tools installed if you don't
already have them set up:

::

    $ xcode-select --install

If you are using OSX, you can use the `Homebrew <http://brew.sh/>`__
system to install Boost (with Python support) and libtorrent:

::

    $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    $ brew install boost-python 
    $ brew install libtorrent-rasterbar --with-python

Installing Inside a Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your virtual environment is using Brew's python:

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

    $ wget http://downloads.sourceforge.net/project/libtorrent/libtorrent/libtorrent-rasterbar-1.0.3.tar.gz
    $ tar -zxvf libtorrent-rasterbar-1.0.3.tar.gz
    $ cd libtorrent-rasterbar-1.0.3
    $ ./configure --disable-debug --disable-dependency-tracking --disable-silent-rules --enable-encryption --prefix=$VIRTUAL_ENV --with-boost-python --enable-dht --with-libiconv --with-boost-libdir=/usr/lib/x86_64-linux-gnu/ --enable-python-binding PYTHON=python PYTHON_LDFLAGS="$(python-config --libs)"
    $ make
    $ make install

You may also need to run:

::

    $ python setup.py install
    $ export LD_LIBRARY_PATH=/usr/local/lib/

Compiling Issues
~~~~~~~~~~~~~~~~

If g++ freezes or errors while building libtorrent, you may not have
enough memory on your instance (can be a problem with small Digital
Ocean instances). You can try to bypass this issue by creating and
enabling a swap file at least 1GB in size:

::

    $ dd if=/dev/zero of=/var/swap.img bs=1024k count=1000
    $ mkswap /var/swap.img
    $ swapon /var/swap.img

Then, try building again.

Windows
-------

If you are on Windows, after you install Boost and libtorrent, you can
use `installation
packages <http://sourceforge.net/projects/libtorrent/files/py-libtorrent/>`__
provided by the libtorrent project to install the Python bindings.

Usage
=====

Generate a New Torrent File
---------------------------

::

    >>> from storjtorrent import StorjTorrent as st

    >>> st.generate_torrent([], shard_directory='../storj/data/myshards')

``generate_torrent()`` is a static method you can use to generate a
torrent file from a specified folder. At a minimum, you will need to
define the folder location. Additional parameters include
``piece_size``, ``pad_size_limit``, ``flags``, ``comment``, ``creator``,
``private``, ``bootstrap_node``, ``bootstrap_port``, ``torrent_name``,
``save_path`` and ``verbose``.

Retrieve Hash of Torrent File
-----------------------------

::

    >>> from storjtorrent import StorjTorrent as st

    >>> st.get_hash([], '../path/to/your/torrentfile')
    'e90e06f2a2461801ac6f7a4b4bccd7f1f16393d3'

``get_hash()`` retrieves the SHA1 hash of the specified torrent file as a libtorrent sha1_hash object. You can apply `.to_str()
to the result to get an encoded string. This string can be used with a magnet link to let others find and download
your torrent via DHT. For example, if the command returns
``e90e06f2a2461801ac6f7a4b4bccd7f1f16393d3``, you could use a
corresponding magnet link of
``magnet:?xt=urn:btih:e90e06f2a2461801ac6f7a4b4bccd7f1f16393d3``.

Adding a Torrent to the Session
-------------------------------

::

    >>> from storjtorrent import StorjTorrent

    >>> st = StorjTorrent()
    >>> st.add_torrent([], '../path/to/your/torrentfile', True)

Once you create a ``StorjTorrent()`` object, a torrent management
session is automatically created for you and awaits the addition of a
torrent. The first string parameter is the local path, magnet link or
URL of the torrent you wish to add. The boolean parameter indicates
whether you are seeding a torrent you created (and have all the data
for). By setting ``seeding=True``, you enable
`super-seeding <https://en.wikipedia.org/wiki/Super-seeding>`__.

Removing a Torrent from the Session
-----------------------------------

::

    >>> st.remove_torrent([], path='../path/to/your.torrent', delete_files=false)

``remove_torrent()`` indicates that StorjTorrent should no longer be
managing this torrent. You can indicate which torrent to stop managing
by passing its corresponding SHA1 hash object (which can be determined
using ``get_hash()``) or path. You also have the option of deleting all
associated torrent data files or not.

Halting a Session
-----------------

::

    >>> st.halt_session()

``halt_session()`` indicates that StorjTorrent should sleep or stop
actively managing torrents. StorjTorrent attempts to automatically
manage its sleep state most of the time. For example, if you remove the
'last' torrent that StorjTorrent was managing, it will automatically put
itself to sleep. If you then add a new torrent, it will 'wake up' again.

It is important to use ``halt_session()`` before you terminate a process
using StorjTorrent as the session management is running in a separate
thread and won't be terminated automatically if it is still managing
torrents.

Retrieving Status of Torrents and Alerts
----------------------------------------

::

    >>> st.get_status()
    {'alerts': ['incoming dht get_peers: ce90f455c3b4928d66006f569b16e2018e405fd2'], 'torrents': {'fake': {'download_rate': 0, 'distributed_copies': -1.0, 'state_str': 'seeding', 'upload_rate': 0, 'progress': 1.0, 'num_peers': 0, 'num_seeds': 0}}}

``get_status()`` returns a dictionary with with an array of ``alerts``
and sub-dictionary of torrent statuses. The status dictionary updates
every five seconds (though this can be reconfigured). The alerts
indicate recent events occuring with StorjTorrent (passed via
libtorrent), such as new DHT peers. The ``torrents`` dictionary contains
information about each torrent that StorjTorrent is managing. It in
cludes information such as download rate, upload rate, state (e.g.
seeding, downloading, uploading, etc.) and overall progress.

.. |Build Status| image:: https://travis-ci.org/Storj/storjtorrent.svg
   :target: https://travis-ci.org/Storj/storjtorrent
.. |Coverage Status| image:: https://img.shields.io/coveralls/Storj/storjtorrent.svg
   :target: https://coveralls.io/r/Storj/storjtorrent
.. |PyPi Version| image:: https://badge.fury.io/py/storjtorrent.svg
   :target: http://badge.fury.io/py/storjtorrent
