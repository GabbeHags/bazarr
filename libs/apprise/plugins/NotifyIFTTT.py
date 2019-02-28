# -*- coding: utf-8 -*-
#
# IFTTT (If-This-Then-That)
#
# Copyright (C) 2019 Chris Caron <lead2gold@gmail.com>
# All rights reserved.
#
# This code is licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# For this plugin to work, you need to add the Maker applet to your profile
# Simply visit https://ifttt.com/search and search for 'Webhooks'
# Or if you're signed in, click here: https://ifttt.com/maker_webhooks
# and click 'Connect'
#
# You'll want to visit the settings of this Applet and pay attention to the
# URL. For example, it might look like this:
#               https://maker.ifttt.com/use/a3nHB7gA9TfBQSqJAHklod
#
# In the above example a3nHB7gA9TfBQSqJAHklod becomes your {apikey}
# You will need this to make this notification work correctly
#
# For each event you create you will assign it a name (this will be known as
# the {event} when building your URL.
import requests

from json import dumps
from .NotifyBase import NotifyBase
from .NotifyBase import HTTP_ERROR_MAP


class NotifyIFTTT(NotifyBase):
    """
    A wrapper for IFTTT Notifications

    """

    # The default descriptive name associated with the Notification
    service_name = 'IFTTT'

    # The services URL
    service_url = 'https://ifttt.com/'

    # The default protocol
    protocol = 'ifttt'

    # A URL that takes you to the setup/help of the specific protocol
    setup_url = 'https://github.com/caronc/apprise/wiki/Notify_ifttt'

    # Even though you'll add 'Ingredients' as {{ Value1 }} to your Applets,
    # you must use their lowercase value in the HTTP POST.
    ifttt_default_key_prefix = 'value'

    # The default IFTTT Key to use when mapping the title text to the IFTTT
    # event. The idea here is if someone wants to over-ride the default and
    # change it to another Ingredient Name (in 2018, you were limited to have
    # value1, value2, and value3).
    ifttt_default_title_key = 'value1'

    # The default IFTTT Key to use when mapping the body text to the IFTTT
    # event. The idea here is if someone wants to over-ride the default and
    # change it to another Ingredient Name (in 2018, you were limited to have
    # value1, value2, and value3).
    ifttt_default_body_key = 'value2'

    # The default IFTTT Key to use when mapping the body text to the IFTTT
    # event. The idea here is if someone wants to over-ride the default and
    # change it to another Ingredient Name (in 2018, you were limited to have
    # value1, value2, and value3).
    ifttt_default_type_key = 'value3'

    # IFTTT uses the http protocol with JSON requests
    notify_url = 'https://maker.ifttt.com/trigger/{event}/with/key/{apikey}'

    def __init__(self, apikey, event, event_args=None, **kwargs):
        """
        Initialize IFTTT Object

        """
        super(NotifyIFTTT, self).__init__(**kwargs)

        if not apikey:
            raise TypeError('You must specify the Webhooks apikey.')

        if not event:
            raise TypeError('You must specify the Event you wish to trigger.')

        # Store our APIKey
        self.apikey = apikey

        # Store our Event we wish to trigger
        self.event = event

        if isinstance(event_args, dict):
            # Make a copy of the arguments so that they can't change
            # outside of this plugin
            self.event_args = event_args.copy()

        else:
            # Force a dictionary
            self.event_args = dict()

    def notify(self, title, body, notify_type, **kwargs):
        """
        Perform IFTTT Notification
        """

        headers = {
            'User-Agent': self.app_id,
            'Content-Type': 'application/json',
        }

        # prepare JSON Object
        payload = {
            self.ifttt_default_title_key: title,
            self.ifttt_default_body_key: body,
            self.ifttt_default_type_key: notify_type,
        }

        # Update our payload using any other event_args specified
        payload.update(self.event_args)

        # Eliminate empty fields; users wishing to cancel the use of the
        # self.ifttt_default_ entries can preset these keys to being
        # empty so that they get caught here and removed.
        payload = {x: y for x, y in payload.items() if y}

        # URL to transmit content via
        url = self.notify_url.format(
            apikey=self.apikey,
            event=self.event,
        )

        self.logger.debug('IFTTT POST URL: %s (cert_verify=%r)' % (
            url, self.verify_certificate,
        ))
        self.logger.debug('IFTTT Payload: %s' % str(payload))
        try:
            r = requests.post(
                url,
                data=dumps(payload),
                headers=headers,
                verify=self.verify_certificate,
            )
            self.logger.debug(
                u"IFTTT HTTP response status: %r" % r.status_code)
            self.logger.debug(
                u"IFTTT HTTP response headers: %r" % r.headers)
            self.logger.debug(
                u"IFTTT HTTP response body: %r" % r.content)

            if r.status_code != requests.codes.ok:
                # We had a problem
                try:
                    self.logger.warning(
                        'Failed to send IFTTT:%s '
                        'notification: %s (error=%s).' % (
                            self.event,
                            HTTP_ERROR_MAP[r.status_code],
                            r.status_code))

                except KeyError:
                    self.logger.warning(
                        'Failed to send IFTTT:%s '
                        'notification (error=%s).' % (
                            self.event,
                            r.status_code))

                # self.logger.debug('Response Details: %s' % r.content)
                return False

            else:
                self.logger.info(
                    'Sent IFTTT notification to Event %s.' % self.event)

        except requests.RequestException as e:
            self.logger.warning(
                'A Connection error occured sending IFTTT:%s ' % (
                    self.event) + 'notification.'
            )
            self.logger.debug('Socket Exception: %s' % str(e))
            return False

        return True

    @staticmethod
    def parse_url(url):
        """
        Parses the URL and returns enough arguments that can allow
        us to substantiate this object.

        """
        results = NotifyBase.parse_url(url)

        if not results:
            # We're done early as we couldn't load the results
            return results

        # Our Event
        results['event'] = results['host']

        # Our API Key
        results['apikey'] = results['user']

        # Store ValueX entries based on each entry past the host
        results['event_args'] = {
            '{0}{1}'.format(NotifyIFTTT.ifttt_default_key_prefix, n + 1):
            NotifyBase.unquote(x)
            for n, x in enumerate(
                NotifyBase.split_path(results['fullpath'])) if x}

        # Allow users to set key=val parameters to specify more types
        # of payload options
        results['event_args'].update(
            {k: NotifyBase.unquote(v)
                for k, v in results['qsd'].items()})

        return results
