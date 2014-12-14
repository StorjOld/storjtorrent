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

from .exception import StorjTorrentError
from .version import __version__
from multiprocessing.dummy import Process
import libtorrent as lt
import os


class Session(object):

    """Libtorrent session management."""

    def __init__(self, port_min=6881, port_max=6891, max_download_rate=0,
                 max_upload_rate=0, save_path='.', allocation_mode='compact',
                 proxy_host='', alert_mask=0xfffffff, verbose=False):
        """Initialize libtorrent session with supplied parameters.

        :param port: Listening port.
        :type port: int
        :param max_download_rate: The maximum download rate given in kB/s.
                                  A value of 0 means the download rate is
                                  unbounded.
        :type max_download_rate: int or float
        :param max_upload_rate: The maximum upload rate given in kB/s. A value
                                of 0 means the upload rate is unbounded.
        :type max_upload_rate: int or float
        :param save_path: The path where the downloaded file/folder should be
                          placed.
        :type save_path: str
        :param allocation_mode: Set the mode used for allocating the downloaded
                                files on disk. Possible options include 'full'
                                and 'compact'.
        :type allocation_mode: str
        :param proxy_host: Sets a HTTP proxy host and port, separate by a
                           colon.
        :type proxy_host: str
        :param alert_mask:  Changes the mask of which alerts to receive. By
                            default only errors are reported. It is a bitmask
                            where each bit represents a category of alerts.
        :type alert_mask: int (bitmask)
        :param verbose: Indicate if actions should be made verbosely or not.
        :type verbose: bool
        """
        if port_min < 0 or port_min > 65525 or not isinstance(port_min, int):
            raise StorjTorrentError(
                'port_min must be an integer value between 0 and 65525.')
        if port_max < port_min or port_max > 65525 or not isinstance(port_max,
                                                                     int):
            raise StorjTorrentError(
                ('port_max must be an integer value greater than port_min and'
                 'less than 65525.'))
        if max_download_rate <= 0:
            self.max_download_rate = -1
        else:
            self.max_download_rate = 1000 * max_download_rate
        if max_upload_rate <= 0:
            self.max_upload_rate = -1
        else:
            self.max_upload_rate = 1000 * max_upload_rate

        self.compact_allocation = allocation_mode == 'compact'

        self.settings = lt.session_settings()
        self.settings.user_agent = 'Storj/' + __version__

        self.session = lt.session()
        self.session.set_download_rate_limit(self.max_download_rate)
        self.session.set_upload_rate_limit(self.max_upload_rate)
        self.session.listen_on(port_min, port_max)
        self.session.set_settings = self.settings
        self.session.set_alert_mask(alert_mask)

        if proxy_host is not '':
            proxy_settings = lt.proxy_settings()
            proxy_settings.type = lt.proxy_type.http
            proxy_settings.hostname = proxy_host.split(':')[0]
            proxy_settings.port = int(proxy_host.split(':')[1])
            self.session.set_proxy(proxy_settings)

        self.handles = []
        self.alerts = []

        self.alive = True
        p = Process(target=self.manage_torrents)
        p.start()
        p.join()

    def add_torrent(self, torrent_location, max_connections=60,
                    max_uploads=-1):
        """ Add a new torrent to be managed by the libtorrent session.

        :param torrent_location: The location of the torrent file. Torrent file
                                 may be located on the local file system or
                                 remotely accessible via the magnet or
                                 http/https protocols.
        :type torrent_location: str
        :param max_connections: Sets the maximum number of connections this
                                torrent will open. If all connections are used
                                up, incoming connections may be refused or poor
                                connetions may be closed. This value must be at
                                least 2. If -1 is given to the function, it
                                means unlimited. There may also be a global
                                limit on the number of connections which may be
                                set using `connections_limit` in self.settings.
        :type max_connections: int
        :param max_uploads: Sets the maximum number of peers that are unchoked
                            at the same time on this torrent. If you set this
                            to -1, there will be no limit. The global maximum
                            upload limit may be set using `unchoke_slots_limit`
                            in self.settings.
        :type max_uploads: int
        """

        if (max_connections < 2 and max_connections is not -1 or
                max_connections is not isinstance(max_connections, int)):
            raise StorjTorrentError(
                'You must have at least two connections per torrent.')

        atp = {}
        atp['save_path'] = self.save_path
        atp['storage_mode'] = lt.storage_mode_t.storage_mode_sparse
        atp['paused'] = False
        atp['auto_managed'] = True
        atp['duplicate_is_error'] = True

        if (torrent_location.startswith('magnet:') or
            torrent_location.startswith('http://') or
                torrent_location.startswith('https://')):
            atp['url'] = torrent_location
        else:
            torrent_info = lt.torrent_info(torrent_location)
            if self.verbose:
                print('Adding \'%s\'...' % torrent_info.name())
            try:
                resume_path = ''.join(
                    [self.save_path, torrent_info.name(), '.fastresume'])
                atp['resume_data'] = open(
                    os.path.join(resume_path), 'rb').read()
            except:
                pass
            atp['ti'] = torrent_info

        handles = self.session.add_torrent(atp)
        self.handles.append(handles)
        handles.set_max_connections(max_connections)
        handles.set_max_uploads(max_uploads)

    def reannounce(self):
        """ Reannounce this torrent to DHT immediately.

        We aren't using trackers for StorjTorrent, otherwise we would use
        force_reannounce() instead.
        """
        for handle in self.handles:
            handle.force_dht_announce()

    def set_alive(self, alive):
        """Indicate whether the session should actively handle torrents or not.

        When a session object is first created, alive is set to True by default
        so you do not need to set it again. You'd only need to reset it after
        changing alive to False.

        :param alive: Boolean value indicating whether session should manage
                      assigned torrents.
        :type alive: bool
        """
        if self.alive is True and alive is False:
            self.alive = False
            self._sleep()
        elif self.alive is False and alive is True:
            self.alive = True
            p = Process(target=self.manage_torrents)
            p.start()
            p.join()

    def pause(self):
        """Pauses all torrents handled by this session."""
        for handle in self.handles:
            handle.pause()

    def resume(self):
        """Resumes all torrents handled by this session."""
        for handle in self.handles:
            handle.resume()

    def _sleep(self):
        """Halt session management of torrents and write resume data."""
        self.pause()
        for handle in self.handles:
            if not handle.is_valid() or not handle.has_metadata():
                continue
            data = lt.bencode(handle.write_resume_data())
            resume_path = os.path.join(self.save_path, ''.join(
                [handle.get_torrent_info().name(), '.fastresume']))
            open(resume_path, 'wb').write(data)

    def manage_torrents(self):
        """Manage all torrents assigned to the session."""
        while self.alive:
            pass
