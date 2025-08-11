import re
import string
import scrapy
from cleantext import clean
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHungYoungBritSpider(BaseSceneScraper):
    name = 'HungYoungBrit'
    network = 'Hung Young Brit'
    parent = 'Hung Young Brit'
    site = 'Hung Young Brit'

    start_urls = [
        'https://www.hungyoungbrit.com',
    ]

    selector_map = {
        'title': '//h3[contains(@class, "title")]/text()',
        'description': '//div[contains(@class, "description")]/p/text()',
        'date': '//h4[contains(text(), "Release")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//video/@poster',
        'performers': '//span[contains(@class, "update_models")]/a/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-thumb")]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('.//a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//h4[contains(text(), "Length")]/text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^0-9a-z]+', '', duration.strip().lower())
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_tags(self, response):
        return ['Gay']

    def get_title(self, response):
        title = super().get_title(response)
        title = title.replace("\n", "").strip()
        title = string.capwords(clean(title, no_emoji=True))
        return title

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("\n", "").strip()
        description = clean(description, no_emoji=True)
        return description

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "Hung Young Brit"
            performer_extra['site'] = "Hung Young Brit"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data
