import re
from datetime import date, timedelta
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
                item['title'] = self.cleanup_title(title)
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

            scenedate = scene.xpath('.//div[@class="sDate"]/text()').get()
            if scenedate:
                if scenedate:
                    item['date'] = self.parse_date(scenedate, date_formats=['%Y-%m-%d']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

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

            days = int(self.days)
            if days > 27375:
                filterdate = "0000-00-00"
            else:
                filterdate = date.today() - timedelta(days)
                filterdate = filterdate.strftime('%Y-%m-%d')

            if self.debug:
                if not item['date'] > filterdate:
                    item['filtered'] = "Scene filtered due to date restraint"
                print(item)
            else:
                if filterdate:
                    if item['date'] > filterdate:
                        yield item
                else:
                    yield item
