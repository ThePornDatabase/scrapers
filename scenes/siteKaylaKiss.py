import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKaylaKissSpider(BaseSceneScraper):
    name = 'KaylaKiss'
    network = 'Kayla Kiss'
    parent = 'Kayla Kiss'
    site = 'Kayla Kiss'

    start_urls = [
        'https://www.kaylakiss.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//div[contains(@class,"videoDetails clear")]//p//text()',
        'image': '',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[@class="label"]/following-sibling::li/a[contains(@href, "/categories/")]/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[@class="date"]/text()').get()
            scenedate = self.parse_date(scenedate, date_formats=['%Y-%m-%d']).strftime('%Y-%m-%d')
            meta['date'] = scenedate

            duration = scene.xpath('.//div[@class="time"]/text()')
            if duration:
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration.get())
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))

            sceneurl = scene.xpath('.//div[1]/a[1]/@href').get()
            if sceneurl:
                meta['url'] = self.format_link(response, sceneurl)

            sceneid = scene.xpath('./div[1]/a[1]//img/@id').get()
            if sceneid:
                meta['id'] = re.search(r'-(\d+)', sceneid).group(1)

            if self.check_item(meta['date'], self.days) and meta['id']:
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        for xpath in [
            '//div[@class="section-video"]//img[contains(@id, "set-target")]/@src0_3x',
            '//div[@class="section-video"]//img[contains(@id, "set-target")]/@src0_2x',
            '//div[@class="section-video"]//img[contains(@id, "set-target")]/@src0_1x',
            '//meta[@property="og:image"]/@content',
        ]:
            image = response.xpath(xpath).get()
            if image:
                return self.format_link(response, image)
        return None