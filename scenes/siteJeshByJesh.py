import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJeshByJeshSpider(BaseSceneScraper):
    name = 'JeshByJesh'
    network = 'JeshByJesh'
    parent = 'JeshByJesh'
    site = 'JeshByJesh'

    start_urls = [
        'https://jeshbyjesh.com',
    ]

    selector_map = {
        'title': '//main/div/h2/text()',
        'description': '//div[@class="blog-content"]/p//text()',
        'date': '//div[contains(@class,"update-info-block")]/span[contains(text(), "RELEASE")]/following-sibling::span[1]/text()',
        'image': '//div[@class="player-thumb"]//img/@src0_1x',
        'performers': '//ul[contains(@class, "model-list")]/li/a//span[contains(@class, "model-list-name")]/text()',
        'tags': '//ul[@class="tags-list"]/li/a/text()',
        'duration': '//div[contains(@class,"update-info-block")]/span[contains(text(), "LENGTH")]/following-sibling::span[1]/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class,"content-card")]')
        for scene in scenes:
            sceneid = scene.xpath('.//img[contains(@id, "set-target")]/@id').get()
            if sceneid:
                meta['id'] = re.search(r'-(\d+)', sceneid).group(1)
            scene_url = scene.xpath('./a[1]/@href').get()
                                    
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene_url), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        return title.replace("•", "-").strip()

    def get_image(self, response):
        image = super().get_image(response)
        if not image or '1x' not in image:
            return image
        for size in ('4x', '3x', '2x'):
            candidate = image.replace('1x', size)
            try:
                r = requests.head(candidate, timeout=10, allow_redirects=True)
                if r.status_code == 200:
                    return candidate
            except requests.RequestException:
                continue
        return image

    def get_tags(self, response):
        title = super().get_title(response)
        tags = super().get_tags(response)
        kept = []
        has_bts = False
        has_interview = False
        for tag in tags:
            if tag in ('Updates', 'Photos', 'Movies'):
                continue
            tlow = tag.lower()
            if tag in title:
                continue
            if 'season' in tlow:
                continue
            if ' id ' in tlow or 'id:' in tlow:
                continue
            if 'bts' in tlow and 'interview' in tlow:
                has_bts = True
                has_interview = True
                continue
            if 'bts' in tlow:
                has_bts = True
                continue
            if 'interview' in tlow:
                has_interview = True
                continue
            kept.append(tag)
        if has_bts:
            kept.append('BTS')
        if has_interview:
            kept.append('Interview')
        return kept