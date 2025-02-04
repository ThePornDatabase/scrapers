import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBratPerversionsSpider(BaseSceneScraper):
    name = 'BratPerversions'
    network = 'Brat Perversions'
    parent = 'Brat Perversions'
    site = 'Brat Perversions'

    start_urls = [
        'https://bratperversions.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//h6[contains(text(), "Added")]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="under-media"]/div[@class="right-side"]/h6/img[contains(@src, "models")]/following-sibling::a/text()',
        'tags': '//div[@class="under-media"]/div[@class="right-side"]/h6/img[contains(@src, "categories")]/following-sibling::a/text()',
        'trailer': '//meta[@itemprop="contentUrl"]/@content',
        'external_id': r'',
        'pagination': '/all-videos/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article')
        for scene in scenes:
            meta['id'] = scene.xpath('./@id').get()
            meta['id'] = re.search(r'(\d+)', meta['id']).group(1)

            scenedate = scene.xpath('.//time[contains(@class, "published")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                    meta['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="under-media"]//h6/img[contains(@src, "clock")]/following-sibling::text()')
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        if re.search(r'http.*?http.*', trailer):
            trailer = re.search(r'http.*?(http.*)', trailer).group(1)
        return trailer
