import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class PenthouseSpider(BaseSceneScraper):
    name = 'Penthouse'
    network = 'Penthouse'
    parent = 'Penthouse'

    start_urls = [
        'https://penthousegold.com'
    ]

    selector_map = {
        'title': '//meta[@itemprop="name"]/@content',
        'description': '//meta[@itemprop="name"]/@content',  # No description on site, just using title for filler
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//ul[@class="scene-models-list"]/li/a/text()',
        'tags': '//ul[@class="scene-tags"]/li/a/text()',
        'external_id': r'\/scenes\/(.+)\.html',
        'trailer': '',  # A trailer is available, but is tokenized and expires
        'pagination': '/categories/videos_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@data-track="SCENE_LINK"]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta={'site': 'Penthouse Gold'})

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        title = title.replace("Video - ", "")
        if title:
            return title.strip().title()
        return ''
