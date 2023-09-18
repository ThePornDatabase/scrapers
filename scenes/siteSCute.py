import re
import string
import scrapy
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSCuteSpider(BaseSceneScraper):
    name = 'SCute'
    network = 'S-Cute'
    parent = 'S-Cute'
    site = 'S-Cute'

    start_urls = [
        'https://www.s-cute.com',
    ]

    selector_map = {
        'title': '//h3[@class="h1"]/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//div[@class="blog-single"]//span[@class="date"]/text()',
        're_date': r'(\d{4}/\d{2}/\d{2})',
        'date_formats': ['%Y/%m/%d'],
        'image': '//div[@class="content-cover"]/img[1]/@src',
        'performers': '',
        'tags': '//div[@class="tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/contents/?&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[@class="contents"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "single-meta")]/div[contains(@class, "pull-left")]/span[@class="comment"]')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_title(self, response):
        title = super().get_title(response)
        title = GoogleTranslator(source='ja', target='en').translate(title.lower())
        title = string.capwords(title)
        return title

    def get_description(self, response):
        description = super().get_title(response)
        description = GoogleTranslator(source='ja', target='en').translate(description)
        return description

    def get_tags(self, response):
        tags = super().get_tags(response)
        new_tags = []
        for tag in tags:
            if tag == "69":
                new_tags.append(tag)
            else:
                tag = GoogleTranslator(source='ja', target='en').translate(tag.lower())
                new_tags.append(string.capwords(tag))
        new_tags.append("Asian")
        new_tags.append("JAV")
        return new_tags
