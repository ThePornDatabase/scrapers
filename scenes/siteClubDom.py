import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClubDomSpider(BaseSceneScraper):
    name = 'ClubDom'
    network = 'Club Dom'
    parent = 'Club Dom'
    site = 'Club Dom'

    start_urls = [
        'https://www.clubdom.com',
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/span[1]/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="gallery_info"]/div[1]/div[1]/div[@class="cell update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//script[contains(text(), "trailer")]/text()',
        're_image': r'df_movie.*?thumbnail:[\'\"](\/.*?\.\w{3,4})[\'\"]',
        'performers': '//div[@class="gallery_info"]/span[contains(@class, "update_description")]/following-sibling::span[@class="update_models"][1]/a/text()',
        'tags': '//span[@class="update_tags"]/a[contains(@href, "/categories/")]/text()',
        'duration': '',
        'trailer': '//script[contains(text(), "trailer")]/text()',
        're_trailer': r'trailer.*?path:[\'\"](.*?\.\w{3,4})[\'\"]',
        'external_id': r'',
        'pagination': '/vod/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('./a[1]/@href').get()
            if meta['id'] and int(meta['id']):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
