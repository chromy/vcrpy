'''Integration tests with httplib2'''
# coding=utf-8

# External imports
import httplib2
from urllib import urlencode
import pytest

# Internal imports
import vcr

from assertions import assert_cassette_empty, assert_cassette_has_one_response


@pytest.fixture(params=["https", "http"])
def scheme(request):
    """
    Fixture that returns both http and https
    """
    return request.param


@pytest.fixture
def http():
    """
    Fixture that returns a configured httplib2 object
    """
    return httplib2.Http()


def test_response_code(http, scheme, tmpdir):
    '''Ensure we can read a response code from a fetch'''
    url = scheme + '://httpbin.org/'
    with vcr.use_cassette(str(tmpdir.join('atts.yaml'))) as cass:
        # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        first, _ = http.request(url, 'GET')
        second, _ = http.request(url, 'GET')
        assert first.status == second.status
        # Ensure that we've now cached a single response
        assert_cassette_has_one_response(cass)


def test_random_body(http, scheme, tmpdir):
    '''Ensure we can read the content, and that it's served from cache'''
    url = scheme + '://httpbin.org/bytes/1024'
    with vcr.use_cassette(str(tmpdir.join('body.yaml'))) as cass:
        # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        assert http.request(url, 'GET')[1] == http.request(url, 'GET')[1]
        # Ensure that we've now cached a single response
        assert_cassette_has_one_response(cass)


def test_response_headers(http, scheme, tmpdir):
    '''Ensure we can get information from the response'''
    url = scheme + '://httpbin.org/'
    with vcr.use_cassette(str(tmpdir.join('headers.yaml'))) as cass:
        # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        first, _ = http.request(url, 'GET')
        second, _ = http.request(url, 'GET')
        assert first.items() == second.items()
        # Ensure that we've now cached a single response
        assert_cassette_has_one_response(cass)


def test_multiple_requests(http, scheme, tmpdir):
    '''Ensure that we can cache multiple requests'''
    urls = [
        scheme + '://httpbin.org/',
        scheme + '://httpbin.org/get',
        scheme + '://httpbin.org/bytes/1024'
    ]
    with vcr.use_cassette(str(tmpdir.join('multiple.yaml'))) as cass:
        for index in range(len(urls)):
            url = urls[index]
            assert len(cass) == index
            assert cass.play_count == index
            assert http.request(url, 'GET')[1] == http.request(url, 'GET')[1]
            assert len(cass) == index + 1
            assert cass.play_count == index + 1


def test_get_data(http, scheme, tmpdir):
    '''Ensure that it works with query data'''
    data = urlencode({'some': 1, 'data': 'here'})
    url = scheme + '://httpbin.org/get?' + data
    with vcr.use_cassette(str(tmpdir.join('get_data.yaml'))) as cass:
    # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        assert http.request(url, 'GET')[1] == http.request(url, 'GET')[1]
        # Ensure that we've now cached a single response
        assert len(cass) == 1
        assert cass.play_count == 1


def test_post_data(http, scheme, tmpdir):
    '''Ensure that it works when posting data'''
    data = urlencode({'some': 1, 'data': 'here'})
    url = scheme + '://httpbin.org/post'
    with vcr.use_cassette(str(tmpdir.join('post_data.yaml'))) as cass:
        # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        _, content1 = http.request(url, 'POST', data)
        _, content2 = http.request(url, 'POST', data)
        assert content1 == content2
        # Ensure that we've now cached a single response
        assert_cassette_has_one_response(cass)


def test_post_unicode_data(http, scheme, tmpdir):
    '''Ensure that it works when posting unicode data'''
    data = urlencode({'snowman': u'☃'.encode('utf-8')})
    url = scheme + '://httpbin.org/post'
    with vcr.use_cassette(str(tmpdir.join('post_data.yaml'))) as cass:
        # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        _, content1 = http.request(url, 'POST', data)
        _, content2 = http.request(url, 'POST', data)
        assert content1 == content2
        # Ensure that we've now cached a single response
        assert_cassette_has_one_response(cass)


def test_cross_scheme(http, tmpdir):
    '''Ensure that requests between schemes are treated separately'''
    # First fetch a url under https, and then again under https and then
    # ensure that we haven't served anything out of cache, and we have two
    # requests / response pairs in the cassette
    with vcr.use_cassette(str(tmpdir.join('cross_scheme.yaml'))) as cass:
        http.request('https://httpbin.org/', 'GET')
        http.request('http://httpbin.org/', 'GET')
        assert len(cass) == 2
        assert cass.play_count == 0

def test_basic_auth(http, scheme, tmpdir):
    '''Check basic auth works'''
    # The 'interesting' way httplib2 does authentication breaks with the
    # default matching rules.
    myvcr = vcr.VCR()
    myvcr.match_on = ['url', 'method', 'headers']

    url = scheme + '://httpbin.org/basic-auth/user/passwd'
    with myvcr.use_cassette(str(tmpdir.join('basic_auth.yaml'))) as cass:
        assert_cassette_empty(cass)
        http.add_credentials('user', 'passwd')
        first, _ = http.request(url, 'GET')
        second, _ = http.request(url, 'GET')
        assert first.status == second.status == 200
