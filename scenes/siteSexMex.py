import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SexMexSpider(BaseSceneScraper):
    name = 'SexMex'
    network = 'SexMex'
    parent = 'SexMex'
    site = 'SexMex'

    start_urls = [
        'https://sexmex.xxx/'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': r'updates/(.*)\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="col-lg-4 col-md-4 col-xs-16 thumb"]')
        for scene in scenes:
            date = scene.xpath('./div/div/p[@class="scene-date"]/text()').get()
            date = self.parse_date(date.strip()).isoformat()
            title = scene.xpath('./div/div/h5/a/text()').get()
            title = title.title()
            if " . " in title:
                title = re.search(r'^(.*) \. ', title).group(1).strip()
            description = scene.xpath(
                './div/div/p[@class="scene-descr"]/text()').get()
            image = scene.xpath('./div/a/img/@src').get()
            image = image.replace(" ", "%20")
            if "transform.php" in image or "url=" in image:
                image = re.search(r'url=(.*)', image).group(1)
            performers = scene.xpath(
                './div/div/p[@class="cptn-model"]/a/text()').getall()

            sceneid = scene.xpath('./@data-setid').get()

            scene = scene.xpath('./div/a/@href').get()
            if sceneid:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     meta={'date': date, 'title': title, 'description': description, 'image': image, 'performers': performers, 'id': sceneid})

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                if trailer.startswith("/"):
                    trailer = "https://sexmex.xxx/" + trailer
                return trailer
        return ''
