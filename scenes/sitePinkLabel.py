import dateparser
import scrapy
import json
import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
import dateparser

class PinkLabelSpider(BaseSceneScraper):
    name = 'PinkLabel'
    network = 'Pink Label'
    parent = 'Pink Label'

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

    def get_trailer(self, repsonse):
        return re.search("http.*\.mp4", repsonse.text).group(0)

    def get_date(self, response):
        metadata = response.xpath("//script[@class='yoast-schema-graph']//text()").get()
        metadata = json.loads(metadata)["@graph"]
        for data in metadata:
            if data["@type"] == "WebPage":
                return dateparser.parse(data["datePublished"]).isoformat()
