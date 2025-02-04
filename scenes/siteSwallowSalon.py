import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSwallowSalonSpider(BaseSceneScraper):
    name = 'SwallowSalon'
    site = 'Swallow Salon'
    parent = 'Swallow Salon'
    network = 'Swallow Salon'

    start_urls = [
        'https://www.swallowsalon.com'
    ]

    selector_map = {
        'title': '//span[@class="title_bar_hilite"]/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//div[@class="gallery_info"]//div[contains(@class,"update_date")]/text()',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//script[contains(text(), "useimage ")]/text()',
        're_image': r'useimage.*?(/content.*?.jpg)',
        'performers': '//div[@class="gallery_info"]//span[@class="update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        meta['check_date'] = "2021-04-09"

        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            scene = scene.xpath('./a[1]/@href').get()
            sceneid = re.search(r'.*/(.*?)\.htm', scene).group(1)
            sceneid = sceneid.lower().replace("_", "-").replace("--", "-")
            meta['id'] = sceneid
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        title_change = re.search(r'^Swallow Salon \w+ (.*)', title)
        if title_change:
            title = title_change.group(1)
        return title

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image, headers={'referer': "https://www.swallowsalon.com/"}, verify=False)
            if req and req.ok:
                return req.content
        return None
