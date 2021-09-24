import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AmatuerBoxxxSpider(BaseSceneScraper):
    name = 'AmateurBoxxx'
    network = 'Amateur Boxxx'
    parent = 'Amateur Boxxx'

    start_urls = [
        'https://tour.amateurboxxx.com'
    ]

    selector_map = {
        'title': 'span.update_title::text',
        'description': 'span.latest_update_description::text',
        'performers': 'span.tour_update_models a::text',
        'date': 'span.availdate::text',
        'image': 'img.large_update_thumb::attr(src)',
        'tags': '',
        'external_id': 'updates/(.+).html',
        'trailer': '',
        'pagination': '/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.css('.updateItem h4 a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
