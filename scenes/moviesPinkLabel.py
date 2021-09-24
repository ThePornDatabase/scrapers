import dateparser
import scrapy
import json
import re
import scrapy
import string

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
import dateparser

class PinkLabelSpider(BaseSceneScraper):
    name = 'PinkLabel'
    network = "PinkLabel"
    parent = "PinkLabel"

    selector_map = {
        'external_id': 'film\\/(.+)\\/',
        'title': '//div[@class="col-md-12 col-sm-8"]/h1/text()',
        'description': '',
        'date': '',
        'image': '//img[@class="img-responsive wp-post-image"]/@src',
        'performers': '//a[contains(@href,"/performer/")]/text()',
        'tags': '//a[contains(@href,"/tag/")]/text()',
        'trailer': '',
    }

    def start_requests(self):
        yield scrapy.Request(url="https://pinklabel.tv/on-demand/studios/", callback=self.get_studios, headers=self.headers, cookies=self.cookies)


    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            return string.capwords(title.strip())
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_studios(self, response):
        '''Request each individual studio page'''
        studios = response.xpath("//div[@class='well']/a/@href")
        for studio in studios:
            yield scrapy.Request(
                url=studio.get(),
                callback=self.get_scenes)

    def get_scenes(self, response):
        '''Request each individual scene page'''
        scenes = response.xpath("//a[@class='epiLink']/@href")
        for scene in scenes:
            yield scrapy.Request(
                url=scene.get().split("?")[0],
                callback=self.parse_scene)

    def get_description(self, response):
        description = response.xpath('//div[@class="ep-description"]/span/p').getall()
        if not isinstance(description, str):
            description = "\n\n".join(description)
        description = re.sub('<[^<]+?>', '', description).strip()
        return description

    def get_trailer(self, response):
        trailer = re.search("http.*\.mp4", response.text)
        if trailer:
            return trailer.group(0)
        return ''

    def get_date(self, response):
        metadata = response.xpath("//script[@class='yoast-schema-graph']//text()").get()
        metadata = json.loads(metadata)["@graph"]
        for data in metadata:
            if data["@type"] == "WebPage":
                return dateparser.parse(data["datePublished"]).isoformat()

    def parse_scene(self, response):
        '''Override studio with correct value'''
        for item in super().parse_scene(response):
            studio = response.xpath('//a[contains(@href,"/studio/")]/text()')[0].get()
            item["parent"] = "PinkLabel"
            item["network"] = "PinkLabel"
            item["site"] = studio
            yield item
