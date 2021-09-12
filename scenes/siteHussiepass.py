import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'hussiepass': "Hussie Pass",
        'povpornstars': "POV Pornstars",
        'seehimfuck': "See Him Fuck",

    }
    return match.get(argument, '')


class HussiepassSpider(BaseSceneScraper):
    name = 'Hussiepass'
    network = "Hussiepass"

    start_urls = [
        'https://www.hussiepass.com',
        'https://povpornstars.com',
        'https://seehimfuck.com'
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '//div[contains(@class,"videoInfo")]/p/span[contains(text(),"Added")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href,"/categories/")]/text()',
        'external_id': '.*\\/(.*?)\\.html',
        'trailer': '//script[contains(text(),"video_content")]',
        'pagination': ''
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(
                response, self.get_selector_map('trailer')).get()
            if trailer:
                base = re.search(
                    r'^http[s]*:\/\/[\w\.]*',
                    response.url).group()
                trailer = base + \
                    re.search('src=\"(.*.mp4)\"', trailer).group(1).strip()
                return trailer
        return ''

    def get_next_page_url(self, base, page):
        if 'hussiepass' in base or 'seehimfuck' in base:
            selector = '/categories/movies/%s/latest/'

        if 'povpornstars' in base:
            selector = '/tour/categories/movies/%s/latest/'

        return self.format_url(base, selector % page)

    def get_site(self, response):
        parsed_uri = tldextract.extract(response.url)
        domain = parsed_uri.domain
        site = match_site(domain)
        if not site:
            site = tldextract.extract(response.url).domain

        return site
