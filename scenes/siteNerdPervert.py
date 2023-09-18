import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNerdPervertSpider(BaseSceneScraper):
    name = 'NerdPervert'
    network = 'NerdPervert'
    parent = 'NerdPervert'
    site = 'NerdPervert'

    start_urls = [
        'https://nerdpervert.com',
    ]

    selector_map = {
        'title': '',
        'description': '//div[@class="story"]//text()',
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=\"(.*?)\"',
        'tags': '',
        'duration': '',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src=\"(.*?)\"',
        'external_id': r'',
        'pagination': '/tour/categories/Videos_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-item")]')
        for scene in scenes:
            scenedate = scene.xpath('.//comment()')
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate.get())
                if scenedate:
                    meta['date'] = scenedate.group(1)
            meta['id'] = scene.xpath('./@data-set-id').get()
            performers = scene.xpath('./h3/a/text()').get().strip()
            if " - " in performers:
                meta['title'] = re.search(r' - (.*)', performers).group(1).strip()
                performers = re.search(r'(.*?) - ', performers).group(1)
                if " and" in performers.lower():
                    meta['performers'] = performers.split(" and ")
                else:
                    meta['performers'] = [performers]
            else:
                meta['title'] = performers.strip()
            scene = scene.xpath('./h3/a/@href').get()
            scene = scene.replace("/updates/", "/trailers/")
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
