import re
import dateparser

import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class PornWorldScraper(BaseSceneScraper):
    name = 'PornWorld'
    network = 'ddfnetwork'

    start_urls = [
        'https://houseoftaboo.com/',
        'https://eurogirlsongirls.com/',
        'https://euroteenerotica.com/',
        'https://ddfbusty.com/',
        'https://1by-day.com/',
        'https://hotlegsandfeet.com/',
        'https://onlyblowjob.com/',
        'https://fuckinhd.com',
    ]

    selector_map = {
        'title': "//meta[@itemprop='name']/@content",
        'description': "//meta[@itemprop='description']/@content",
        'date': "//meta[@itemprop='uploadDate']/@content",
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': "//div[contains(@class,'pornstar-card')]//meta[@itemprop='name']/@content",
        'tags': "ul.tags a::text",
        'external_id': 'videos\\/[A-Z-_a-z0-9+]+\\/(\\d+)',
        'trailer': '//meta[@itemprop="contentUrl"]/@content',
        'pagination': '/videos/search/latest/ever/allsite/-/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//*[@id='scenesAjaxReplace']//a/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date.replace('Released:', '').replace('Added:', '').strip()
            return dateparser.parse(date.strip()).isoformat()
        else:
            date = response.xpath('//div[@id="video-specs"]/div/div/div[contains(@class, "d-inline-flex")]/p/text()').get()
            if re.match('\d{2}.\d{2}.\d{4}', date):
                return dateparser.parse(date.strip()).isoformat()
