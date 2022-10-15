import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrandNewAmateursVODSpider(BaseSceneScraper):
    name = 'BrandNewAmateursVOD'
    network = 'Brand New Amateurs'
    parent = 'Brand New Amateurs'
    site = 'Brand New Amateurs'

    start_urls = [
        'https://www.brandnewamateurs.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="row"]/div[@class="cell update_date"][1]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '',
        'performers': '',
        'tags': '//meta[@name="keywords"]/@content',
        'trailer': '//script[contains(text(), "df_movie.length")]/text()',
        're_trailer': r'df_movie.length.*?path\:\"(.*?.mp4)',
        'external_id': r'.*/(.*?).html',
        'pagination': '/vod/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]/a[1]')
        for scene in scenes:
            image = scene.xpath('.//img/@src0_2x')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        if ";;" in title:
            title = re.search(r'(.*?);;', title).group(1)
        return title
