import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMyDeepDarkSecretSpider(BaseSceneScraper):
    name = 'MyDeepDarkSecret'
    network = 'My Deep Dark Secret'
    parent = 'My Deep Dark Secret'
    site = 'My Deep Dark Secret'

    start_urls = [
        'https://mydeepdarksecret.com',
    ]

    selector_map = {
        'title': '//h2[@itemprop="headline"]/text()',
        'description': '//span[@itemprop="about"]//text()',
        'date': '',
        'image': '//div[@class="playerC"]/video/@poster',
        'performers': '//span[@itemprop="actors"]/a/text()',
        'tags': '//span[@itemprop="keywords"]/a/text()',
        'trailer': '//div[@class="playerC"]/video/source/@src',
        'external_id': r'.*/(.*)/',
        'pagination': '/scenes/page/%s/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="latestVid"]/ul/li/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        image = response.xpath(self.get_selector_map('image'))
        if image:
            image = image.get()
            sceneyear = re.search(r'uploads/(\d{4})', image)
            if sceneyear:
                sceneyear = sceneyear.group(1)
            scenemonth = re.search(r'uploads/\d{4}/(\d{2})', image)
            if scenemonth:
                scenemonth = scenemonth.group(1)
            if sceneyear and scenemonth:
                return f"{sceneyear}-{scenemonth}-01T00:00:00"
        return self.parse_date('today').isoformat()

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Scenes" in tags:
            tags.remove("Scenes")
        return tags
