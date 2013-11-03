"""A Python wrapper for the DigitalOcean API."""

import sys
python_major_version = sys.version_info[0]

import json
from itertools import chain, cycle, islice

import requests


class APIException(Exception):
    """This is thrown when an DigitalOcean API request returns an error."""

    def __init__(self, resource_path, api_msg):
        self.resource_path = resource_path
        self.api_msg = api_msg

    def __str__ (self):
        msg = 'While getting https://{}{}, DigitalOcean reported an error' + \
            ':\n\t"{}"'
        return msg.format(
            DigitalOceanAPI.api_host, self.resource_path, self.api_msg)


class DigitalOceanAPI(object):
    """This is a general wrapper around the DigitalOcean API.

    See README.md for example usage.

    TODO:
        - Improve error reporting: Misuse of the request() command, such as by
          passing the wrong number of ids for a given api endpoint, results in
          an APIException (good!) that can be hard to decipher (bad!).

    """

    api_host = "api.digitalocean.com"

    def __init__(
        self,
        client_id,
        api_key,
        check_cert = True,
        pemfile = None,
        capath = None,
        maximum_retries=2,
        debug=False
    ):
        """Create a DigitalOceanAPI instance.

        Keyword Arguments:
            check_cert - whether the HTTPS connection's cert should be verified
            pemfile - path to PEM file, such as "/etc/ssl/certs/ca-certificates.pem"
            capath - path to list of CA certs, such as "/etc/ssl/certs/"

        Note:
            To use the DigitalOceanAPI class, you must provide either a
            pemfile or a capath. If it is not obvious which values to provide,
            see http://mercurial.selenic.com/wiki/CACertificates for a related
            explanation and platform-specific hints.

        """

        assert client_id
        assert api_key
        assert pemfile or capath if check_cert else True
        assert maximum_retries >= 0

        self.connection = None
        self.client_id = client_id
        self.api_key = api_key
        self.pemfile = pemfile
        self.capath = capath
        self.check_cert = check_cert
        self.maximum_retries = maximum_retries
        self._retries_count = maximum_retries
        self._debug = debug

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    def request(self, api_endpoint, params={}, ids=[]):
        """Perform an API request and returns the parsed JSON data.

        Throws an exception with API description if the response is an error.

        Arguments:
            api_endpoint -
                API endpoints are documented at
                https://www.digitalocean.com/api

                IMPORTANT NOTE:
                    When DigitalOcean specifies endpoints that require ids,
                    their documenation shows the ids inline as they appear in
                    the HTTP GET request. For example, '/images/[image_id]' or
                    '/domains/[domain_id]/records/new'. s

                    To keep things simple for you, the api_endpoint parameter
                    omits the placeholders for the ids, the ids themselves,
                    and the leading front slash.

                    So, for example:
                        when DigitalOcean says:
                            /domains

                        set api_endpoint to:
                            'domains'


                        when DigitalOcean says:
                            /images/[image_id]/destroy

                        set api_endpoint to:
                            'images/destroy'


                        when DigitalOcean says:
                            /domains/[domain_id]/records/[record_id]/destroy

                        set api_endpoint to:
                            'domains/records/destroy'

            params - parameters of the request EXCLUDING client_id and api_key
                e.g., {'name': 'domain_name', 'ip_address': '127.0.0.1'}

            ids - array of ids for endpoints that require an id or two
                Example endpoints that require ids:
                    /droplets/[droplet_id]/reboot requires one id
                    /domains/[domain_id]/records/[record_id] requires two ids

                The array must contain the ids required by the endpoint in the
                order they appear in the endpoint.

        """

        resource_path = self._make_resource_path(api_endpoint, params, ids)

        try:
            response = requests.get("https://{}{}".format(
                DigitalOceanAPI.api_host, resource_path))
        except requests.exceptions.RequestException as e:
            return self._retry_or_raise(api_endpoint, params, ids, e)

        if response.status_code != 200:
            raise APIException(resource_path, 'status code: {}'.format(
                response.status_code))

        self._retries_count = 0

        try:
            response_json = response.json()
        except ValueError:
            raise APIException(
                self._make_resource_path(
                    api_endpoint, params, ids, redact_credentials=True),
                response_data)

        if response_json["status"] != "OK":
            raise APIException(
                self._make_resource_path(
                    api_endpoint, params, ids, redact_credentials=True),
                response_json["message"])

        return response_json


    def _make_resource_path(
        self, api_endpoint, params={}, ids=[], redact_credentials=False
    ):
        path = '/'

        try:
            path += '/'.join(self._roundrobin(api_endpoint.split('/'), ids))
        except KeyError:
            path += api_endpoint

        # TODO: We should have a separate redact_credentials() method that
        # can be applied to any paths instead of this conditional.
        credentials = {
            'client_id': self.client_id,
            'api_key': self.api_key
        } if not redact_credentials else {
            'client_id': '[REDACTED]',
            'api_key': '[REDACTED]'
        }

        all_params = dict(chain(params.items(), credentials.items()))
        path_params = '&'.join(
            ['{}={}'.format(k,v) for (k,v) in all_params.items()])

        return '{}{}?{}'.format(
            path,
            '/' if '/' not in path else '',
            path_params)

    def _roundrobin(self, *iterables):
        """roundrobin('ABC', 'D', 'EF') --> A D E B F C"""
        # Based upon a recipe credited to George Sakkis.
        # Source: http://docs.python.org/3.3/library/itertools.html
        pending = len(iterables)

        if python_major_version == 3:
            nexts = cycle(iter(it).__next__ for it in iterables)
        else:
            nexts = cycle(iter(it).next for it in iterables)

        while pending:
            try:
                for next in nexts:
                    yield str(next())
            except StopIteration:
                pending -= 1
                nexts = cycle(islice(nexts, pending))

    def _retry_or_raise(self, api_endpoint, params, ids, exception):
        if self._retries_count < self.maximum_retries:
            self._retries_count += 1
            return self.request(api_endpoint, params, ids)
        else:
            raise exception.__class__(' -- '.join(
                [
                    'https://{}{}'.format(
                        DigitalOceanAPI.api_host,
                        self._make_resource_path(
                            api_endpoint,
                            params,
                            ids,
                            redact_credentials=True)),
                    str(exception)
                ]
            ))