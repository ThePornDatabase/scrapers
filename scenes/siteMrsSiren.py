import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMrsSirenSpider(BaseSceneScraper):
    name = 'MrsSiren'
    network = 'Mrs Siren'
    parent = 'Mrs Siren'
    site = 'Mrs Siren'

    start_urls = [
        'https://mrssiren.com',
    ]

    selector_map = {
        'title': '',
        'description': '//div[@class="content"]/p/span/following-sibling::text()',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*)?\.html',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videoBlock"]')
        for scene in scenes:
            scenelink = scene.xpath('./div/a/@href').get()
            title = scene.xpath('./div/a/text()').getall()
            title = " ".join(title).replace("  ", " ").strip()
            image = scene.xpath('./div/a/img/@src0_3x').get()
            image_blob = self.get_image_blob_from_link(image)
            sceneid = re.search(r'.*/(.*)-', image).group(1)
            performers = scene.xpath('./p/a/text()').getall()
            scenedate = scene.xpath('.//comment()')
            if scenedate:
                scenedate = " ".join(scenedate.getall())
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate)
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y']).isoformat()
            if sceneid:
                if "signup" in scenelink:
                    scenelink = 'https://mrssiren.com/tour/trailers/' + re.sub(r"[^a-zA-Z0-9 -]", "", title).replace(" ", "-") + ".html"
                yield scrapy.Request(url=self.format_link(response, scenelink), callback=self.parse_scene, meta={'image': image, 'date': scenedate, 'performers': performers, 'title': title, 'id': sceneid, 'image_blob': image_blob})
