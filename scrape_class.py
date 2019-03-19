import requests
import time
import fake_useragent
from itertools import cycle
from lxml.html import fromstring
from stem import Signal
from stem.control import Controller
import cfscrape
import logging
try:
     # Python 2.6-2.7
    from HTMLParser import HTMLParser
except ImportError:
    # Python 3
    from html.parser import HTMLParser

logger = logging.getLogger(__name__)


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:100000]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)

    return proxies


def set_new_ip():
    """Change IP using TOR"""
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='shashank')
        controller.signal(Signal.NEWNYM)
        controller.close()
    print("Done setting new IP")

proxies = get_proxies()
proxy_pool = cycle(proxies)
USE_TOR = False


class UserAgent:
    """
    User-Agent handling retries and errors ...
    """

    # UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    def __init__(self, baseurl, retry=0, retrydelay=6000):
        self.baseurl, self.retry, self.retrydelay = baseurl, retry, retrydelay
        self.initialize()

    def initialize(self):
        self.session = requests.session()
        self.ua_choice = fake_useragent.UserAgent()

    def get(self, path, params={}, headers={}):
        new_headers = self.session.headers.copy()
        new_headers.update(headers)
        scraper = cfscrape.create_scraper()
        http_proxy = {'http': '127.0.0.1:8118'} # "127.0.0.1:8118"

        if USE_TOR:
            old_ip = "0.0.0.0"
            new_ip = "0.0.0.0"
            nbr_of_ip_addresses = 3
            seconds_between_checks = 2


            if new_ip != "0.0.0.0":
                old_ip = new_ip
            new_ip = requests.get("http://icanhazip.com/", proxies=http_proxy).text
            print("beginIP = %s" % new_ip)
            set_new_ip()
            new_ip = requests.get("http://icanhazip.com/", proxies=http_proxy).text
            print("Call to newIP made. newIP = %s" % new_ip)
            seconds = 0

            while old_ip == new_ip:
                time.sleep(seconds_between_checks)
                seconds += seconds_between_checks
                new_ip = requests.get("http://icanhazip.com/", proxies=http_proxy).text
                print("New IP generated: %s :: %d seconds elapsed awaiting a different IP address." % (new_ip, seconds))
            print("here")
            print("newIP: %s" % new_ip)

        # _e = None
        for attempt in range(self.retry):
            try:
                if not USE_TOR:
                    proxy = next(proxy_pool)
                    http_proxy = {'http': proxy}

                self.session.headers.update({"user-agent": self.ua_choice.random})
                print(self.ua_choice.random)
                resp = scraper.get("%s%s%s"%(self.baseurl, "/" if not path.startswith("/") else "", path))
                '''
                resp = requests.get("%s%s%s"%(self.baseurl, "/" if not path.startswith("/") else "", path),
                                         proxies=http_proxy, headers=new_headers)
                '''

                if resp.status_code != 200:
                    print("failed get..")
                    raise Exception("Unexpected Status Code: %s!=200; Status msg: %s" % (resp.status_code, resp.text))
                return resp
            except Exception as e:
                logger.exception(e)
                #_e = e

            # GET has failed
            retry_delay = self.retrydelay + 10*(attempt)
            logger.warning("Retrying in %d seconds..." % retry_delay)
            time.sleep(retry_delay)

        raise Exception("get exhausted its retries")

    def post(self, path, params={}, headers={}):
        new_headers = self.session.headers.copy()
        new_headers.update(headers)
        for _ in range(self.retry):
            try:
                resp = self.session.post("%s%s%s"%(self.baseurl, "/" if not path.startswith("/") else "", path),
                                        params=params, headers=new_headers)
                if resp.status_code != 200:
                    raise Exception("Unexpected Status Code: %s!=200; Status msg: %s" % (resp.status_code, resp.text))
                return resp
            except Exception as e:
                logger.exception(e)
            logger.warning("Retrying in %d seconds..." % self.retrydelay)
            time.sleep(self.retrydelay)
        raise e