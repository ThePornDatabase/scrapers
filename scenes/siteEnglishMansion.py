import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEnglishMansionSpider(BaseSceneScraper):
    name = 'EnglishMansion'
    network = 'EnglishMansion'
    parent = 'EnglishMansion'
    site = 'EnglishMansion'

    selector_map = {
        'description': '//p[@class="synopsis"]/text()',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}

        url = "https://www.theenglishmansion.com/updates_ajax.html?type=latest"
        yield scrapy.Request(url, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//td[contains(text(), "Movie Update")]//ancestor::table[1]')
        for scene in scenes:
            item = self.init_scene()
            item['title'] = self.cleanup_title(scene.xpath('.//p[@class="title"]/text()').get())

            scenedate = scene.xpath('.//td[contains(@class, "block-title") and contains(text(), ", ")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d+\w{1,2}? \w+ \d{4})', scenedate)
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%d %B, %Y']).strftime('%Y-%m-%d')

            performers = scene.xpath('.//p[@class="featuring"]/text()')
            if performers:
                performers = performers.get().lower()
                performers = performers.replace("featuring", "").replace("&amp;", "&").strip()
                if "&" in performers:
                    performers = performers.split("&")
                else:
                    performers = [performers]
                item['performers'] = list(map(lambda x: string.capwords(x.replace("lady ", "").replace("miss ", "").replace("mistress ", "").strip()), performers))

            item['description'] = super().get_description(scene)

            image = scene.xpath('.//p[@class="cover"]/img[1]/@src')
            if image:
                image = "https://www.theenglishmansion.com/" + image.get().replace(".com//still", ".com/still")
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'.*/(.*)\.', image).group(1)
                if "_blur" in item['id']:
                    item['id'] = item['id'].replace("_blur", "")

            item['url'] = "https://www.theenglishmansion.com/videos/" + item['id']
            item['id'] = item['id'].lower()
            item['tags'] = ['Female Domination']

            item['site'] = 'English Mansion'
            item['parent'] = 'English Mansion'
            item['network'] = 'English Mansion'
            item['type'] = "Scene"

            yield item
