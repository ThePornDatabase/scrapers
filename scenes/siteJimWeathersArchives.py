import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJimWeathersArchivesSpider(BaseSceneScraper):
    name = 'JimWeathersArchives'
    network = 'Jim Weathers Archives'
    parent = 'Jim Weathers Archives'
    site = 'Jim Weathers Archives'

    start_urls = [
        'https://www.jimweathersarchives.com',
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/span/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="gallery_info"]/div[@class="table"]/div[@class="row"]/div[@class="cell update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="gallery_info"]/span[@class="update_models"]/a/text()',
        'tags': '//div[@class="gallery_info"]/span[@class="update_tags"]/a/text()',
        'trailer': '//script[contains(text(), "df_movie")]/text()',
        're_trailer': r'df_movie.*?(/store.*?\.mp4)',
        'external_id': r'.*/(\w{2,5}\-?\d{3,4})',
        'pagination': '/store/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        description = super().get_description(response)
        if "Photo Set:" in description:
            description = re.sub(r'Photo Set:\s+?\w+\d+$', '', description)
        return description.strip()
