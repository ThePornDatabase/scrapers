import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTheLisaAnnSpider(BaseSceneScraper):
    name = 'TheLisaAnn'
    network = 'The Lisa Ann'
    parent = 'The Lisa Ann'
    site = 'The Lisa Ann'

    start_urls = [
        'https://thelisaann.com',
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/span/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="gallery_info"]/div[@class="table"]/div/div[contains(@class, "date")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="gallery_info"]/span[contains(@class, "update_models")]/a/text()',
        'tags': '//div[@class="gallery_info"]/span[contains(@class, "update_tags")]/a/text()',
        'duration': '',
        'trailer': '//script[contains(text(), "trailer")]/text()',
        're_trailer': r'trailer.*?path:[\'\"](.*?)[\'\"]',
        'external_id': r'',
        'pagination': '/vod/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            duration = scene.xpath('.//div[contains(@class,"update_counts")]/text()')
            if duration:
                duration = duration.get()
                duration = duration.replace("&nbsp;", "").replace(" ", "").lower()
                duration = re.sub(r'[^a-z0-9]', '', duration)
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    meta['duration'] = str(int(duration.group(1)) * 60)
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('./a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
