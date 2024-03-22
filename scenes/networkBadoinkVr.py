from datetime import datetime
import dateparser
import scrapy
import re
from tpdb.items import SceneItem
from tpdb.BaseSceneScraper import BaseSceneScraper


class BadoinkVrSpider(BaseSceneScraper):
    name = 'BadoinkVr'
    network = 'Badoink VR'
    parent = 'Badoink VR'
    max_pages = 100
    start_urls = [
        'https://badoinkvr.com',
        'https://babevr.com',
        'https://18vr.com',
        'http://kinkvr.com',
        'https://vrcosplayx.com',
        'https://realvr.com',
    ]

    selector_map = {
        'title': '//h1[@itemprop="name"]/@content | //h1[contains(@class, "video-title")]/text()',
        'description': '//p[@itemprop="description"]/@content | //p[@class="video-description"]/text()',
        'date': '//p[@itemprop="uploadDate"]/@content | //p[@class="video-upload-date"]/text()',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content | //img[@class="video-image"]/@src',
        'performers': '//a[contains(@class, "video-actor-link")]/text()',
        'tags': "//p[@class='video-tags']//a/text()",
        'external_id': '-(\\d+)\\/?$',
        'trailer': ''
    }

    def get_scenes(self, response):
        scenes = response.xpath("//div[@class='tile-grid-item']//a[contains(@class, 'video-card-title')]/@href").getall()
        for scene in scenes:
            scene = self.format_link(response, scene)
            yield scrapy.Request(scene, callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        selector = '/vrpornvideos/%s?order=newest'

        if 'vrbtrans' in base:
            selector = '/videos/?category=all&sort=latest&page=%s'
        elif 'vrcosplay' in base:
            selector = '/cosplaypornvideos/%s?order=newest'
        elif 'kinkvr' in base:
            selector = '/bdsm-vr-videos/%s?order=newest'

        return self.format_url(base, selector % page)

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).get()
        if date:
            return dateparser.parse(date.strip()).isoformat()
        return datetime.now().isoformat()

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', self.get_date(response)).group(1)
        item['image'] = self.get_image(response)
        if item['image']:
            item['image_blob'] = self.get_image_blob(response)
        else:
            item['image_blob'] = ""

        if item['image']:
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.network
        item['parent'] = item['site']

        item['type'] = 'Scene'
        yield self.check_item(item, self.days)
