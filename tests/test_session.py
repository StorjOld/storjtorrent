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

from storjtorrent import Session
from storjtorrent import StorjTorrentError
from storjtorrent import IntervalTimer
import libtorrent as lt
import pytest
import threading
import os
import pdb

REMOTE_TORRENT = 'http://releases.ubuntu.com/14.04.1/'
'ubuntu-14.04.1-desktop-amd64.iso.torrent'
REMOTE_HASH = 'cb84ccc10f296df72d6c40ba7a07c178a4323a14'
REMOTE_MAGNET = ''.join(['magnet:?xt=urn:btih:', REMOTE_HASH])


@pytest.fixture(scope='function', params=[True, False])
def default_session(request):
    os.chdir('tests')
    s = Session(verbose=request.param)

    def fin():
        s.set_alive(False)
        os.chdir('../')
    request.addfinalizer(fin)
    return s


@pytest.fixture(scope='function', params=[True, False])
def session_with_torrent(request):
    os.chdir('tests')
    s = Session(verbose=request.param)
    s.add_torrent('data.torrent', seeding=True)

    def fin():
        s.set_alive(False)
        os.chdir('../')
    request.addfinalizer(fin)
    return s


class TestSession:

    def session_thread_count(self):
        return [isinstance(thread, IntervalTimer) for thread
                in threading.enumerate()].count(True)

    @pytest.mark.parametrize('min', [-1, 65526, 'shoe'])
    def test_init_port_min(self, min):
        with pytest.raises(StorjTorrentError):
            Session(port_min=min)

    @pytest.mark.parametrize('min,max',
                             [(80, 70), (80, 65526), (80, 'beatboxing')])
    def test_init_port_max(self, min, max):
        with pytest.raises(StorjTorrentError):
            Session(port_min=min, port_max=max)

    @pytest.mark.parametrize('max_download_rate', [-100, 0])
    def test_init_max_download_rate_less_equal_zero(self, max_download_rate):
        s = Session(max_download_rate=max_download_rate)
        assert s.max_download_rate == -1
        s.set_alive(False)

    def test_init_max_download_rate_greater_zero(self):
        max_download_rate = 500
        s = Session(max_download_rate=max_download_rate)
        assert s.max_download_rate == 1000 * max_download_rate
        s.set_alive(False)

    @pytest.mark.parametrize('max_upload_rate', [-100, 0])
    def test_init_max_upload_rate_less_equal_zero(self, max_upload_rate):
        s = Session(max_upload_rate=max_upload_rate)
        assert s.max_upload_rate == -1
        s.set_alive(False)

    def test_init_max_upload_rate_greater_zero(self):
        max_upload_rate = 500
        s = Session(max_upload_rate=max_upload_rate)
        assert s.max_upload_rate == 1000 * max_upload_rate
        s.set_alive(False)

    def test_init_proxy_host_exists(self, default_session):
        proxy = default_session.session.proxy()
        assert proxy.type is 0
        assert proxy.hostname is ''
        assert proxy.port is 0

    def test_init_proxy_host_not_exists(self):
        s = Session(proxy_host='loveboat.org:8123')
        proxy = s.session.proxy()
        assert proxy.type is 4
        assert proxy.hostname == 'loveboat.org'
        assert proxy.port == 8123
        s.set_alive(False)

    def test_set_alive_from_alive_to_dead(self, default_session):
        default_session.set_alive(False)
        assert default_session.alive is False

    def test_set_alive_from_dead_to_alive(self, default_session):
        default_session.set_alive(False)
        thread_count = self.session_thread_count()
        default_session.set_alive(True)
        assert self.session_thread_count() is thread_count + 1
        assert default_session.alive is True

    @pytest.mark.parametrize('max_connections', [1, -2, 'chicken'])
    def test_add_torrent_bad_max_connections(self, default_session,
                                             max_connections):
        torrent_location = 'http://fake.com/fake.torrent'
        with pytest.raises(StorjTorrentError):
            default_session.add_torrent(torrent_location, max_connections)

    @pytest.mark.timeout(5)
    def test_add_torrent_and_seed(self, session_with_torrent, capsys):
        out, err = capsys.readouterr()
        if session_with_torrent.verbose is True:
            assert 'Adding' in out
        else:
            assert out == ''
        assert len(session_with_torrent.handles) is 1
        while len(session_with_torrent._status['torrents']) is 0:
            pass
        assert session_with_torrent._status['torrents']['data']['state_str']\
            is 'seeding'

    @pytest.mark.timeout(5)
    def test_add_torrent_and_download(self, default_session):
        default_session.add_torrent(REMOTE_TORRENT)
        assert len(default_session.handles) is 1
        while len(default_session._status['torrents']) is 0:
            pass
        assert default_session._status['torrents'].popitem()[1]['state_str']\
            == 'downloading metadata'

    @pytest.mark.timeout(5)
    def test_add_magnet_and_download(self, default_session):
        default_session.add_torrent(REMOTE_MAGNET)
        assert len(default_session.handles) is 1
        while len(default_session._status['torrents']) is 0:
            pass
        assert default_session._status['torrents'].popitem()[1]['state_str']\
            == 'downloading metadata'

    def test_pause_torrents(self, session_with_torrent):
        session_with_torrent.pause()
        assert session_with_torrent.handles[0].is_paused()

    def test_resume_torrents(self, session_with_torrent):
        handle = session_with_torrent.handles[0]
        session_with_torrent.pause()
        assert handle.is_paused()
        session_with_torrent.resume()
        assert not handle.is_paused()

    def test_remove_torrent(self, session_with_torrent):
        assert len(session_with_torrent.handles) is 1
        info_hash = lt.torrent_info(
            lt.bdecode(open('data.torrent', 'rb').read())).info_hash()
        session_with_torrent.remove_torrent(info_hash)
        assert len(session_with_torrent.handles) is 0

    @pytest.mark.timeout(5)
    def test_get_status(self, session_with_torrent):
        while 'data' not in session_with_torrent.get_status()['torrents']:
            pass
        assert session_with_torrent.get_status()[
            'torrents']['data']['state_str'] is 'seeding'


# test: reannounce
# test: sleep (and see that fastresume written)
