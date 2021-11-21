import re
import html

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteColetteSpider(BaseSceneScraper):
    name = 'Colette'
    network = "BC Media"
    parent = "Colette"

    start_urls = [
        'https://www.colette.com',
    ]

    cookies = {
        '_warning': 'true',
    }

    selector_map = {
        'title': '//div[@class="row info"]/div/h1/text()',
        'description': '//div[@class="row"]/div/p//text()',
        'date': '//div[@class="row"]/div/h2[1]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[contains(@class,"video-tour")]//img/@data-interchange',
        're_image': r'.*\[(http.*lrg.jpg)',
        'performers': '//div[@class="row"]/div/h2/span/following-sibling::a/text()',
        'tags': '',
        'external_id': r'.*/(.*?)/$',
        'trailer': '',
        'pagination': '/index.php?show=videos&pref=items&page=%s&catname=&order=recent'
    }

    def get_scenes(self, response):
        scene_text = response.text.replace('\\/', '/').replace('\\"', '"')
        scenes = re.findall('href=\"(https.*?videos.*?)\"', scene_text)
        for scene in scenes:
            scene = scene.replace(" ", "%20")
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Colette"

    def get_description(self, response):

        description = response.xpath(self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            if description:
                description = description.replace('HD Video: ', '')
                return html.unescape(description.strip())
        return ''

    def get_id(self, response):
        externid = super().get_id(response)
        externid = externid.replace("%20", "-").lower()
        return externid
