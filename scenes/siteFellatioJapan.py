import re
import string
import html
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFellatioJapanSpider(BaseSceneScraper):
    name = 'FellatioJapan'
    network = 'Digital J Media'
    parent = 'Fellatio Japan'

    start_urls = [
        'https://www.fellatiojapan.com/'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': "",
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': '',
        'trailer': '',
        'pagination': ''
    }

    def start_requests(self):
        url = "https://www.fellatiojapan.com/en/girls"
        yield scrapy.Request(url, callback=self.get_scenes,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//span/a[contains(@href,"girl/")]/@href').getall()
        for scene in scenes:
            scene = "https://www.fellatiojapan.com/en/" + scene
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_model_scenes)

    def parse_model_scenes(self, response):

        scenes = response.xpath('//div[contains(@class,"scene-obj")]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./span[@class="sGirl"]//text()').getall()
            if title:
                title = " ".join(title)
                item['title'] = html.unescape(string.capwords(title.strip()))
            else:
                item['title'] = ''

            item['description'] = ''

            performers = scene.xpath('./span[@class="sGirl"]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip(), performers))
            else:
                item['performers'] = []

            tags = scene.xpath('.//a[contains(@href,"tag")]/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: x.strip().title(), tags))
            else:
                item['tags'] = []

            date = scene.xpath('.//div[@class="sDate"]/text()').get()
            if date:
                if date:
                    item['date'] = dateparser.parse(date, date_formats=['%Y-%m-%d']).isoformat()
            else:
                item['date'] = []

            image = scene.xpath('.//div[@class="scene-img"]/@style').get()
            if image:
                image = re.search(r'(http.*\.jpg)', image).group(1)
                if image:
                    item['image'] = image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            extern_id = scene.xpath('.//div[@class="scene-hover"]/@data-path').get()
            if extern_id:
                item['id'] = extern_id.strip()
                item['trailer'] = "https://cdn.fellatiojapan.com/preview/" + item['id'] + "/hover.mp4"

            item['site'] = "Fellatio Japan"
            item['parent'] = "Fellatio Japan"
            item['network'] = "Digital J Media"

            item['url'] = response.url

            yield item

    def get_site(self, response):
        return "After School.jp"
