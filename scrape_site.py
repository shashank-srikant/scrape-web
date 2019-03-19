from scrape_class import UserAgent
from bs4 import BeautifulSoup
import time


class ScrapeAPI:
    def __init__(self):
        self.session = UserAgent(baseurl="https://www.somewebsite.com", retry=5, retrydelay=5)

    def get_page_info(self, address):
        html = self.session.get("/address/%s#code" % address).text

        # The following is just dummy code
        parsed_html = BeautifulSoup(html, 'lxml')
        source_raw = parsed_html.body.find('pre', attrs={'class': 'js-sourcecopyarea'})

        if source_raw is None:
            source_raw = ''
        else:
            source_raw = source_raw.text

        source_byte = parsed_html.body.find('div', attrs={'id': 'verifiedbytecode2'})
        source_other = parsed_html.body.find('pre', attrs={'id': 'js-copytextarea2'})
        return [source_raw, source_byte, source_other]


def scrape():
    s = ScrapeAPI()
    s.get_page_info("some sub URL")
    time.sleep(3)
