import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteOpenLifeSpider(BaseSceneScraper):
    name = 'OpenLife'
    network = 'Open Life'
    parent = 'Open Life'
    site = 'Open Life'

    start_urls = [
        'https://www.openlife.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/en/videos/All/views/0/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "imageRotation")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = json.loads(response.xpath('//script[contains(@type, "ld+json")]/text()').get())
        jsondata = jsondata[0]
        item = SceneItem()
        item['title'] = jsondata['name']
        item['id'] = re.search(r'.*/(\d+)', response.url).group(1)
        if 'description' in jsondata:
            item['description'] = jsondata['description']
        else:
            item['description'] = ""
        if "keywords" in jsondata:
            item['tags'] = jsondata['keywords'].split(",")
        else:
            item['tags'] = []
        item['image'] = response.xpath('//meta[@name="twitter:image"]/@content').get()
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['date'] = jsondata['dateCreated']
        item['trailer'] = None
        item['type'] = 'Scene'
        item['network'] = "Open Life Network"
        item['performers'] = []
        if "actor" in jsondata:
            for actor in jsondata['actor']:
                item['performers'].append(actor['name'])
        item['site'] = self.get_site(response)
        item['parent'] = self.get_site(response)
        item['url'] = response.url
        if "duration" in jsondata:
            item['duration'] = self.duration_to_seconds(jsondata['duration'].replace("PT", ""))
        else:
            item['duration'] = ""
        yield self.check_item(item, self.days)

    def get_site(self, response):
        site = response.xpath('//div[contains(@id, "sceneInfo")]/div[contains(@class, "sceneInfoCol")]/div/@class')
        if site:
            site = site.get()
            if site.strip().lower() == "sitelogo_40":
                return "Abbey Brooks"
            if site.strip().lower() == "sitelogo_37":
                return "Ashley Fires"
            if site.strip().lower() == "sitelogo_38":
                return "Devon Lee"
            if site.strip().lower() == "sitelogo_34":
                return "Dylan Ryder"
            if site.strip().lower() == "sitelogo_36":
                return "Hanna Hilton"
            if site.strip().lower() == "sitelogo_2":
                return "Lane Sisters"
            if site.strip().lower() == "sitelogo_1":
                return "Open Life"
            if site.strip().lower() == "sitelogo_64":
                return "Sunny Leone"
            if site.strip().lower() == "sitelogo_45":
                return "Teal Conrad"
        return "Open Life"
