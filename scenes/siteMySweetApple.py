import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMySweetAppleSpider(BaseSceneScraper):
    name = 'MySweetApple'
    network = 'MySweetApple'
    parent = 'MySweetApple'
    site = 'MySweetApple'

    start_urls = [
        'https://www.mysweetapple.com',
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/span/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="gallery_info"]/div[@class="table"]/div[@class="row"]/div[contains(@class,"update_date")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="gallery_info"]/span[@class="update_models"]/a/text()',
        'tags': '//div[@class="gallery_info"]/span[@class="update_tags"]/a/text()',
        'trailer': '//script[contains(text(), "sourcetrailer")]/text()',
        're_trailer': r'sourcetrailer.*?path\:\"(.*?\.mp4)',
        'external_id': r'.*/(.*)\.htm',
        'pagination': '/ppv/updates/page_%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="latest_updates_block"][1]//div[@class="update_details"]')
        for scene in scenes:
            link = self.format_link(response, scene.xpath('./a[1]/@href').get())
            sceneid = scene.xpath('./@data-setid')
            if sceneid:
                meta['id'] = sceneid.get().strip()
            else:
                imagesrc = scene.xpath('.//a//img/@id').get()
                print(imagesrc)
                print(link)
                meta['id'] = re.search(r'.*-(\d+)', imagesrc).group(1)
            if 'id' in meta:
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace('\r', ' ').replace('\t', ' ').replace('\n', ' ').replace('  ', ' ').strip()
        return description
