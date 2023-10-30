import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteKimHollandDateSpider(BaseSceneScraper):
    name = 'KimHollandDate'
    network = 'Kim Holland'
    parent = 'Kim Holland'
    site = 'Kim Holland'

    start_urls = [
        'https://www.kimholland.nl',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/zoeken--%s.html',
        'type': 'Scene',
        'force_update': True,
        'force_fields': 'date'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="movie-item-search"]')
        for scene in scenes:
            item = SceneItem()
            item['force_update'] = True
            item['force_fields'] = 'date'
            item['title'] = self.cleanup_title(scene.xpath('./div/a[1]/text()').get())
            item['description'] = self.cleanup_description(scene.xpath('./div/p[1]/text()').get())
            item['image'] = ''
            item['image_blob'] = ''
            item['date'] = scene.xpath('.//span[contains(@class,"search-date")]/text()').get()
            item['site'] = 'Kim Holland'
            item['parent'] = 'Kim Holland'
            item['network'] = 'Kim Holland'
            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''
            item['url'] = self.format_link(response, scene.xpath('./a[1]/@href').get())
            item['id'] = re.search(r'.*-(\d+)\.htm', item['url']).group(1)
            yield self.check_item(item, self.days)
