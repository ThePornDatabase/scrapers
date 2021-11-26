import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteJavHubSpider(BaseSceneScraper):
    name = 'JavHub'
    network = 'JavHub'
    parent = 'JavHub'
    site = 'JavHub'

    start_urls = [
        'https://tour.javhub.com',
    ]

    selector_map = {
        'title': '//div[@class="row"]/div/h5[contains(@class, "mt-3")]/text()',
        'description': '//p[@class="MsoNormal"]/text()',
        'date': '//span[@class="date"]/text()',
        'image': '//div[contains(@class, "ypp-video-player-wrap")]//video/@poster',
        'performers': '//span[contains(text(), "Starring")]/following-sibling::a/text()',
        'tags': '',
        'external_id': r'videos/(\d+)/.*',
        'trailer': '',
        'pagination': '/scenes?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"content-item")]')
        for scene in scenes:
            sceneurl = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), sceneurl):
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene)
            elif "/join" in sceneurl:
                item = SceneItem()

                title = scene.xpath('.//h3[@class="title"]/a/text()')
                if title:
                    item['title'] = self.cleanup_title(title.get())
                else:
                    item['title'] = ''

                scenedate = scene.xpath('.//span[@class="pub-date"]/text()')
                if scenedate:
                    scenedate = scenedate.get()
                    scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate)
                    if scenedate:
                        item['date'] = self.parse_date(scenedate.group(1), date_formats=['%B %d, %Y']).isoformat()
                else:
                    item['date'] = self.parse_date('today').isoformat()

                image = scene.xpath('./div/a/@data-images')
                if image:
                    image = re.search(r'(http.*?\.jpg)', image.get().replace("\\", "")).group(1)
                    item['image'] = self.format_link(response, image)
                    externalid = re.search(r'.*/(\w{8,15}?)/.*', item['image']).group(1)
                    item['id'] = externalid.lower()
                else:
                    item['image'] = ''
                    externalid = item['title'].replace(" ", "-").lower()
                    item['id'] = re.sub('[^a-zA-Z0-9-]', '', externalid)

                performers = scene.xpath('.//h4[@class="models"]/a/text()')
                if performers:
                    item['performers'] = list(map(lambda x: x.strip().title(), performers.getall()))
                else:
                    item['performers'] = []

                item['description'] = ''
                item['image_blob'] = None
                item['tags'] = ['Asian']
                item['trailer'] = ''
                item['url'] = response.url
                item['network'] = 'JavHub'
                item['parent'] = 'JavHub'
                item['site'] = 'JavHub'

                if item['id'] and item['title']:
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

    def get_tags(self, response):
        return ['Asian']

    def get_description(self, response):
        description = super().get_description(response)
        return description.replace("\r", "").replace("\n", " ").replace("\t", " ")
