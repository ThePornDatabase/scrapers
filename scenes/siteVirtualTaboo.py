import re
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteVirtualTabooSpider(BaseSceneScraper):
    name = 'VirtualTaboo'
    network = 'POVR'
    parent = 'Virtual Taboo'
    site = 'Virtual Taboo'

    start_urls = [
        'https://virtualtaboo.com',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="video-item"]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//div[contains(@class, "video-title")]/a/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = None

            scenedate = scene.xpath('.//div[@class="info"]/span[@class="bullet"][2]/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r"(\d{1,2} \w+, \d{4})", scenedate)
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%d %B, %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            performers = scene.xpath('.//div[@class="info"]/span[@class="bullet"][1]/following-sibling::a/text()')
            if performers:
                item['performers'] = list(map(lambda x: self.cleanup_title(x), performers.getall()))
            else:
                item['performers'] = []

            tags = scene.xpath('.//div[@class="tag-list"]/a/text()')
            if tags:
                item['tags'] = list(map(lambda x: self.cleanup_title(x), tags.getall()))
                words = ['4k', '5k', '6k', '7k', '8k']
                for word in words:
                    if word in item['tags']:
                        item['tags'].remove(word)
            else:
                item['tags'] = ['VR Porn']

            image = scene.xpath('./div[contains(@class, "images-container")]/div[contains(@class, "left-col")]/a/@data-lazy-bg')
            if image:
                image = image.get()
                if "?p" in image:
                    image = re.search(r'(.*?\.jpg)\?p', image).group(1)
                    item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            description = scene.xpath('.//div[@class="description"]/span/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())
            else:
                item['description'] = ''

            url = scene.xpath('./div[contains(@class, "images-container")]/div[contains(@class, "left-col")]/a/@href')
            if url:
                item['url'] = self.format_link(response, url.get())
                item['id'] = re.search(r'.*/(.*?)$', item['url']).group(1)
            else:
                item['url'] = response.url
                item['id'] = None

            item['image_blob'] = None
            item['trailer'] = None
            item['network'] = 'POVR'
            item['parent'] = 'POVR'
            item['site'] = 'Virtual Taboo'
            if item['title'] and item['id'] and item['date'] > '2021-02-13':
                if "days" in self.settings:
                    days = int(self.settings['days'])
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.isoformat()
                else:
                    filterdate = "0000-00-00"

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
