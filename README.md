# StorjTorrent

StorjTorrent is a wrapper library for libtorrent's Python bindings. It allows Storj packages to create torrents, seed files to other Storj nodes, and retrieve files using their hashes.

# Building

You will need to ensure [Boost](http://www.boost.org/) is properly installed so you can properly build and install `libtorrent`:

    $ wget http://sourceforge.net/projects/boost/files/boost/1.57.0/boost_1_57_0.tar.gz
    $ tar -zxvf boost_*.tar.gz
    $ cd boost_*
    $ ./bootstrap.sh
    $ ./b2
    $ sudo ./b2 install

After Boost is successfully built, you can build and install `libtorrent`:

    $ wget http://downloads.sourceforge.net/project/libtorrent/libtorrent/libtorrent-rasterbar-1.0.3.tar.gz
    $ tar -zxvf libtorrent-*.tar.gz
    $ cd libtorrent-rasterbar-1.0.3
    $ ./configure --enable-python-binding
    $ make
    $ sudo make install

You may also need to run:

    $ cd bindings/python
    $ sudo python setup.py install

## OSX

You may need to have XCode's command line tools installed if you don't already have them set up:

    $ xcode-select --install

If you are using OSX, you can use the [Homebrew](http://brew.sh/) system to install Boost (with Python support) and libtorrent:

    $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    $ brew install boost-python 
    $ brew install libtorrent-rasterbar --with-python

### Installing Inside a Virtual Environment

Ensure your virtual environment is using Brew's python:

    $ mkvirtualenv -p /usr/local/bin/python storjtorrent

If you are installing inside a virtual environment, you can try the following (after you install boost-python with homebrew):

    $ brew install boost-build
    $ wget http://downloads.sourceforge.net/project/libtorrent/libtorrent/libtorrent-rasterbar-1.0.3.tar.gz
    $ tar -zxvf libtorrent-*.tar.gz
    $ cd libtorrent-rasterbar-1.0.3
    $ ./configure --disable-debug --disable-dependency-tracking --disable-silent-rules --enable-encryption --prefix=$VIRTUAL_ENV --with-boost=/usr/local/opt/boost --enable-python-binding --with-libiconv --with-boost-python=boost_python-mt PYTHON=python PYTHON_LDFLAGS="$(python-config --libs)"
    $ make
    $ make install

## Ubuntu

Install supporting tools and libraries:

    $ apt-get install build-essential
    $ apt-get install source python-libtorrent
    $ apt-get build-dep python-libtorrent

Create a new virtual environment. For example, if you have `virtualenvwrapper` installed, you can use the following to create and enter a new virtual environment called `storjtorrent`:

    $ mkvirtualenv storjtorrent

Then, once inside the virtual environment, run the following commands:

    $ wget http://downloads.sourceforge.net/project/libtorrent/libtorrent/libtorrent-rasterbar-1.0.3.tar.gz
    $ tar -zxvf libtorrent-rasterbar-1.0.3.tar.gz
    $ cd libtorrent-rasterbar-1.0.3
    $ ./configure --with-boost-python --enable-dht --with-boost-libdir=/usr/lib/x86_64-linux-gnu/ --enable-python-binding
    $ make
    $ make install
    $ cd bindings/python
    $ python setup.py build
    $ python setup.py install
    $ export LD_LIBRARY_PATH=/usr/local/lib/

### Compiling Issues

If g++ freezes or errors while building libtorrent, you may not have enough memory on your instance (can be a problem with small Digital Ocean instances). You can try to bypass this issue by creating and enabling a swap file at least 1GB in size:

    $ dd if=/dev/zero of=/var/swap.img bs=1024k count=1000
    $ mkswap /var/swap.img
    $ swapon /var/swap.img

Then, try building again.

## Windows

If you are on Windows, after you install Boost and libtorrent, you can use [installation packages](http://sourceforge.net/projects/libtorrent/files/py-libtorrent/) provided by the libtorrent project to install the Python bindings.

# Usage

## Generate a New Torrent File

    from storjtorrent import StorjTorrent as st

    st.generate_torrent([], shard_directory='../storj/data/myshards')

`generate_torrent()` is a static method you can use to generate a torrent file from a specified folder. At a minimum, you will need to define the folder location. Additional parameters include `piece_size`, `pad_size_limit`, `flags`, `comment`, `creator`, `private`, `bootstrap_node`, `bootstrap_port`, `torrent_name` and `verbose`.

TODO: Document all methods.