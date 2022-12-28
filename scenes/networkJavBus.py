import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class JavBusSpider(BaseSceneScraper):
    name = 'JavBus'
    network = 'JavBus'
    parent = 'JavBus'

    start_urls = [
        'https://www.javbus.com'
    ]

    selector_map = {
        'title': "#videos_page-page h1::text",
        'date': '//div[@class="col-md-3 info"]/p[2]/text()',
        'image': '//a[contains(@href, "/cover/")]/@href | //a[@class="sample-box"]/div/img/@src',
        'performers': '//a[@class="avatar-box"]//span/text()',
        'tags': '//span[@class="genre"]/a[contains(@href, "/genre/")]/text()',
        'external_id': '\\/([0-9A-Za-z_-]+)$',
        'trailer': '',
        'pagination': '/en/uncensored/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.css(".movie-box::attr(href)").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_site(self, response):
        return response.xpath(
            '//p/a[contains(@href, "/studio/")]/text()').get().strip()

    def get_title(self, response):
        title = response.xpath(
            '//head/title/text()').get().strip().replace(' - JavBus', '')
        externid = self.get_id(response)
        if externid.replace('-', '').replace('_', '').replace(' ', '').isdigit():
            title = self.get_site(response) + ' ' + title
            title = title.replace(externid + ' ', '')

        return title

    def parse_scene(self, response):
        item = SceneItem()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob(response)
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['markers'] = self.get_markers(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = self.get_parent(response)
        item['type'] = 'Scene'

        if "pondo" not in item['site'].lower():
            yield self.check_item(item, self.days)
