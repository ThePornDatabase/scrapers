import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkAdultPrimeSpider(BaseSceneScraper):
    name = 'AdultPrime'
    network = 'Adult Prime'

    start_urls = [
        'https://adultprime.com',
    ]

    selector_map = {
        'title': '//h2[@class="update-info-title"]/text()',
        'description': '//p[contains(@class,"ap-limited-description-text")]/text()',
        'date': '//p[contains(@class,"update-info-line")]/i[@class="fa fa-calendar"][1]/following-sibling::b[1]/text()',
        'date_formats': ['%m.%d.%Y'],
        'image': '//div[contains(@class,"update-video-wrapper")]/a/div/@style',
        're_image': r'(http.*\.jpg)',
        'performers': '//b[contains(text(), "Performer")]/following-sibling::a/text()',
        'tags': '//b[contains(text(), "Niches")]/following-sibling::text()',
        'external_id': r'.*/(\d+)',
        'trailer': '',
        'pagination': '/studios/videos?q=&website=&niche=&year=&type=&sort=&page=%s#focused'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="row portal-grid"]//div[@class="overlay-wrapper"]/div[1]/a/@href').getall()
        for scene in scenes:
            sceneid = re.search(r'Id=(\d+)', scene)
            if sceneid:
                sceneid = sceneid.group(1)
                scene = "https://adultprime.com/studios/video/" + sceneid
                yield scrapy.Request(scene, callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//b[contains(text(), "Studio")]/a[1]/text()')
        if site:
            site = site.get()
        else:
            site = "AdultPrime"
        return site.strip()

    def get_parent(self, response):
        site = response.xpath('//b[contains(text(), "Studio")]/a[1]/text()')
        if site:
            site = site.get()
        else:
            site = "AdultPrime"
        return site.strip()

    def get_tags(self, response):
        tags = response.xpath('//b[contains(text(), "Niches")]/following-sibling::text()')
        if tags:
            tags = tags.get()
            tags = tags.split(",")
            tags = list(map(lambda x: x.strip(), tags))
            if "" in tags:
                tags.remove("")
        return tags
