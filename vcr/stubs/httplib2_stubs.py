'''Stubs for httplib2'''

from httplib2 import HTTPConnectionWithTimeout, HTTPSConnectionWithTimeout, \
    CA_CERTS
from ..stubs import VCRHTTPSConnection, VCRHTTPConnection


class VCRHTTPSConnectionWithTimeout(VCRHTTPSConnection, HTTPSConnectionWithTimeout):
    _baseclass = HTTPSConnectionWithTimeout

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=None, proxy_info=None,
                 ca_certs=None, disable_ssl_certificate_validation=False):
        VCRHTTPSConnection.__init__(self, host, port=port,
                                         key_file=key_file,
                                         cert_file=cert_file, strict=strict)
        self.timeout = timeout
        self.proxy_info = proxy_info
        if ca_certs is None:
            ca_certs = CA_CERTS
        self.ca_certs = ca_certs
        self.disable_ssl_certificate_validation = \
                disable_ssl_certificate_validation

class VCRHTTPConnectionWithTimeout(VCRHTTPConnection, HTTPConnectionWithTimeout):
    _baseclass = HTTPConnectionWithTimeout
    def __init__(self, host, port=None, strict=None, timeout=None, proxy_info=None):
        VCRHTTPConnection.__init__(self, host, port, strict)
        self.timeout = timeout
        self.proxy_info = proxy_info

