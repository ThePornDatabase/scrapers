import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDarkkoTVSpider(BaseSceneScraper):
    name = 'DarkkoTV'
    network = 'DarkkoTV'
    parent = 'DarkkoTV'
    site = 'DarkkoTV'

    start_urls = [
        'https://darkkotv.com',
    ]

    selector_map = {
        'description': '//div[@class="vidImgTitle"]//div[contains(@class, "vidImgContent ")]//text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="vidImgTitle"]//p[@class="link_light"]/a/text()',
        'tags': '//div[@class="vidImgTitle"]//div[contains(@class, "blogTags")]/ul/li/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="latestUpdateB"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[contains(i/@class, "calendar")]/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                meta['date'] = self.parse_date(scenedate, date_formats=['%m-%d-%Y']).strftime('%Y-%m-%d')

            meta['id'] = scene.xpath('./@data-setid').get()

            title = scene.xpath('.//h4/a/text()')
            if title:
                meta['title'] = string.capwords(title.get().strip())

            sceneurl = scene.xpath('.//h4/a/@href')

            if meta['id'] and self.check_item(meta, self.days):
                yield scrapy.Request(url=self.format_link(response, sceneurl.get()), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="vidImgTitle"]//i[contains(@class, "fa-video")]/following-sibling::text()[contains(., "min")]')
        if duration:
            duration = duration.get().strip()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
    
    def get_image(self, response):
        image = super().get_image(response)
        if image and "-2x" in image:
            image = image.replace("-2x", "-4x")
            return image
        return None