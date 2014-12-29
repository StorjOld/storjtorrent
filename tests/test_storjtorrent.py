#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Josh Brandoff
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from storjtorrent import StorjTorrent
from storjtorrent import StorjTorrentError
import pytest
import os


@pytest.fixture(scope='function')
def st(request):
    os.chdir('tests')
    s = StorjTorrent()

    def fin():
        s.halt_session()
        for path in ['data.fastresume', 'storj.torrent']:
            os.remove(path) if os.path.exists(path) else None
        os.chdir('../')
    request.addfinalizer(fin)
    return s


@pytest.fixture(scope='function', params=[True, False])
def st_with_torrent(request):
    os.chdir('tests')
    st = StorjTorrent()
    st.add_torrent('data.torrent', request.param)

    def fin():
        st.halt_session()
        for path in ['data.fastresume', 'storj.torrent']:
            os.remove(path) if os.path.exists(path) else None
        os.chdir('../')
    request.addfinalizer(fin)
    return st


class TestStorjTorrent:

    def test_initialize_storjtorrent(self, st):
        assert st.session.alive is True

    @pytest.mark.parametrize('isSeeding', [True, False, ])
    def test_add_torrent_alive(self, st, isSeeding):
        st.add_torrent('data.torrent', isSeeding)
        assert len(st.session.handles) is 1

    @pytest.mark.parametrize('isSeeding', [True, False, ])
    def test_add_torrent_dead(self, st, isSeeding):
        st.halt_session()
        st.add_torrent('data.torrent', isSeeding)
        assert st.session.alive is True

    def test_remove_torrent_by_filename(self, st_with_torrent):
        st_with_torrent.remove_torrent_by_filename('data.torrent')
        assert len(st_with_torrent.session.handles) is 0

    def test_halt_session(self, st):
        st.halt_session()
        assert st.session.alive is False

    @pytest.mark.timeout(5)
    def test_get_status(self, st_with_torrent):
        while 'data' not in st_with_torrent.get_status()['torrents']:
            pass
        assert True

    def test_get_torrent_hash(self, st):
        target_hash = '994bab2df24af5297d86d48abf9fb13bc49b8cb2'
        raw_hash = st.get_hash('data.torrent')
        encoded_hash = str(raw_hash)
        assert encoded_hash is target_hash

    @pytest.mark.parametrize('verbose', [True, False, ])
    def test_generate_torrent_bad_piece_size(self, st, verbose):
        with pytest.raises(StorjTorrentError):
            st.generate_torrent('data', piece_size=1000, verbose=verbose)

    @pytest.mark.parametrize('verbose', [True, False, ])
    def test_generate_torrent_empty_dir(self, st, tmpdir, verbose):
        with pytest.raises(StorjTorrentError):
            st.generate_torrent(tmpdir, verbose=verbose)

    @pytest.mark.parametrize('verbose', [True, False, ])
    def test_generate_torrent_success(self, st, verbose):
        st.generate_torrent('data', verbose=verbose)
        assert os.path.exists('storj.torrent')
