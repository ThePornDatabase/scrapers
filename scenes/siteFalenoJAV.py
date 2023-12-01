import re
import string
import scrapy
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFalenoJAVSpider(BaseSceneScraper):
    name = 'FalenoJAV'
    network = 'Faleno'
    parent = 'Faleno'
    site = 'Faleno'

    start_urls = [
        'https://faleno.jp',
    ]

    selector_map = {
        'title': '//div[@class="bar02"]/h1/text()',
        'description': '//div[@class="box_works01_text"]/p/text()',
        'date': '//div[@class="box_works01"]/div[contains(@class,"box_works01_list")]/ul[2]/div[@class="view_timer"][3]/li/p/text()',
        'image': '//div[@class="box_works01_img"]/a/img/@src',
        'performers': '//div[contains(@class,"box_works01_list")]/ul[1]/li[1]/p/text()',
        'tags': '',
        'trailer': '//div[@class="box_works01_img"]/a/@href',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/top/work/page/%s/',
        'type': 'JAV',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@data-mh="group01"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        if len(performers) == 1:
            performers = performers[0].split("/")
        performers2 = []
        for performer in performers:
            performer = GoogleTranslator(source='ja', target='en').translate(performer.lower())
            performers2.append(string.capwords(performer.strip()))
        return performers2

    def get_description(self, response):
        description = super().get_description(response)
        description = GoogleTranslator(source='ja', target='en').translate(description)
        description = re.sub(r'[^a-zA-Z0-9 \'-_:!\?\.,/\\]', " ", description)
        description = description.replace("  ", " ").replace("  ", " ").strip()
        return description

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"box_works01_list")]/ul[1]/li[2]/p/text()')
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                duration = str(int(duration.group(1)) * 60)
        return duration

    def get_id(self, response):
        scene_id = super().get_id(response).lower()
        scene_id = re.sub(r'[^a-z0-9-]', "", scene_id)
        if "-" not in scene_id:
            scene_id = re.search(r'([a-z]*)(\d*)', scene_id)
            scene_id = scene_id.group(1) + "-" + scene_id.group(2)
        return scene_id

    def get_title(self, response):
        title = super().get_title(response)
        title = GoogleTranslator(source='ja', target='en').translate(title.lower())
        title = re.sub(r'[^a-zA-Z0-9 \'-_:!\?]', " ", title)
        title = title.replace("  ", " ").replace("  ", " ").strip()
        title = string.capwords(title)
        title = self.get_id(response).upper() + " - " + title
        return title

    def get_tags(self, response):
        return ['Asian']

    def get_image(self, response):
        image = super().get_image(response)
        if "?" in image:
            image = re.search(r'(.*)\?', image).group(1)
        return image
