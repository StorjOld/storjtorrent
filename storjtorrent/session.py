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
import libtorrent as lt


class Session(object):

    """Libtorrent session management."""

    def __init__(self, port_min=6881, port_max=6891, max_download_rate=0,
                 max_upload_rate=0, save_path='.', allocation_mode='compact',
                 proxy_host='', alert_mask=0xfffffff):
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
