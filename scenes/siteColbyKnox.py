import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteColbyKnoxSpider(BaseSceneScraper):
    name = 'ColbyKnox'
    network = 'Colby Knox'
    parent = 'Colby Knox'
    site = 'Colby Knox'

    start_urls = [
        'https://www.colbyknox.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-detail-title")]/h1/text()',
        'description': '//h2[contains(text(), "Description")]/following-sibling::p/text()',
        'date': '',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//div[@class="model-tip-info"]/div/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '//meta[@itemprop="contentUrl"]/@content',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-block-wrapper")]')
        for scene in scenes:
            duration = scene.xpath('.//i[contains(@class, "fa-clock")]/following-sibling::text()')
            if duration:
                duration = duration.get()
                meta['duration'] = self.duration_to_seconds(duration.strip())
            meta['tags'] = ['Gay']
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        image = super().get_image(response)
        date = re.search(r'images/(\d{8})', image)
        if date:
            date = date.group(1)
            date = self.parse_date(date, date_formats=['%Y%m%d']).strftime('%Y-%m-%d')
            return date
        return None
