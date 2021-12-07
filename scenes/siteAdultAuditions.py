import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAdultAuditionsSpider(BaseSceneScraper):
    name = 'AdultAuditions'
    network = 'Adult Auditions'
    parent = 'Adult Auditions'
    site = 'Adult Auditions'

    start_urls = [
        'https://adultauditions.co',
    ]

    selector_map = {
        'title': '//div[@class="col-sm-8"]/h3/text()',
        'description': '//div[@class="col-sm-4"]/h4[contains(text(), "Description")]/following-sibling::p/text()',
        'date': '',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//div[@class="col-sm-4"]/h3/a/text()',
        'tags': '',
        'external_id': r'vref=(.*)',
        'trailer': '',
        'pagination': '/adultauditions.php?p=%s&i=20&f=1&o=1'
    }

    def start_requests(self):
        url = 'https://adultauditions.co'
        yield scrapy.Request(url, callback=self.start_requests_2, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="col-sm-3"]/a')
        for scene in scenes:
            image = scene.xpath('./img/@src')
            if image:
                image = image.get()
                if image:
                    if image[0] == ".":
                        image = image[1:]
                        image = self.format_link(response, image).replace(" ", "%20")
                    else:
                        image = None
            else:
                image = None
            scene = scene.xpath('./@href').get()
            if scene[0] == ".":
                scene = scene[1:]
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image})

    def get_tags(self, response):
        return ['Amateur', 'Audition']
