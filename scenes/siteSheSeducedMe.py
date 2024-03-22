import re
import scrapy
import html
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSheSeducedMeSpider(BaseSceneScraper):
    name = 'SheSeducedMe'
    site = 'She Seduced Me'
    parent = 'She Seduced Me'
    network = 'She Seduced Me'

    start_urls = [
        'https://sheseducedme.com',
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/span/text()',
        'description': '//span[contains(@class,"update_description")]/text()',
        'date': '//div[contains(@class, "gallery_info")]/div[1]//div[contains(@class,"update_date")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="page_body"]/div[@class="gallery_info"]/span[@class="update_models"]/a/text()',
        'tags': '//div[@class="page_body"]/div[@class="gallery_info"]/span[@class="update_tags"]/a/text()',
        'trailer': '//script[contains(text(), "df_movie")]/text()',
        're_trailer': r'df_movie.*?path.*?[\'\"](.*?)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/vod/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@id, "packageinfo")]')
        for scene in scenes:
            duration = scene.xpath('./following-sibling::div[contains(@class, "update_counts")]')
            if duration:
                duration = duration.get()
                duration = unidecode.unidecode(html.unescape(duration.lower().replace("&nbsp;", " ").replace("\xa0", " ")))
                duration = re.sub('[^a-zA-Z0-9-/]', '', duration)
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    meta['duration'] = str(int(duration.group(1)) * 60)

            scene = scene.xpath('./following-sibling::a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = super().get_id(response)
        sceneid = sceneid.lower()
        if "_vids" in sceneid:
            sceneid = re.search(r'(.*?)_vids', sceneid).group(1)
        return sceneid
