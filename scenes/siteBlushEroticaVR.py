import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlushEroticaVRSpider(BaseSceneScraper):
    name = 'BlushEroticaVR'
    network = 'BlushEroticaVR'
    parent = 'BlushEroticaVR'
    site = 'BlushEroticaVR'

    start_urls = [
        'https://blusheroticavr.com',
    ]

    selector_map = {
        'title': '//div[@class="vidImgTitle"]/h4/text()',
        'description': '//div[contains(@class,"vidImgContent")]/p/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="vidImidWrap"]//a[contains(@class,"link_bright") and contains(@href, "/models/")]/text()',
        'tags': '//div[@class="blogTags"]/ul//a[@class="border_btn"]/text()',
        'duration': '//div[contains(@class,"latestUpdateBinfo") and contains(@class, "gallery_info")]/ul[@class="videoInfo"]/li[@class="text_med" and contains(text(), "min")]',
        're_duration': r'(\d+)\s*min',
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="latestUpdateB"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get().strip()
            scenedate = scene.xpath('.//ul[@class="videoInfo"]/li[contains(text(), "/")]/text()')
            if scenedate:
                scenedate = self.parse_date(scenedate.get().strip(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
                meta['date'] = scenedate
            sceneurl = scene.xpath('.//div[@class="videoPic"]/a[1]/@href').get()

            if self.check_item(meta, self.days) and meta['id']:
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if image:
            return image.replace("-2x", "-4x")
        return None
    
    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = [tag for tag in tags if 'blush' not in tag.lower()]
        if 'VR' not in tags:
            tags.append('VR')
        return tags
    
    def get_duration(self, response):
        duration = response.xpath(self.selector_map['duration']).get()
        if duration:
            match = re.search(self.selector_map['re_duration'], duration)
            if match:
                return int(match.group(1)) * 60
        return 0