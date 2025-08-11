import re
from requests import get
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBigLatinAnalSpider(BaseSceneScraper):
    name = 'BigLatinAnal'
    network = 'Big Latin Anal'
    parent = 'Big Latin Anal'
    site = 'Big Latin Anal'

    start_urls = [
        'https://www.biglatinanal.com/home/home.html',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
    }

    def start_requests(self):
        meta = {}

        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//section[@class="modelo"]')
        for scene in scenes:
            item = self.init_scene()

            performer = scene.xpath('./div[@class="global"]/span[1]/text()')
            performer = re.sub(r'[^A-Za-z ]+', '', performer.get())
            item['performers'] = [string.capwords(performer.strip())]

            title = scene.xpath('./div[@class="global"]/h2/text()').get()
            title = re.sub(r'[^A-Za-z -]+', '', title)
            item['title'] = title
            item['title'] = string.capwords(item['title'])

            image = scene.xpath('./div[contains(@class,"imagenes")]/div[2]/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image'] = item['image'].replace("../", "")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'(\d+)\.', item['image']).group(1).lstrip("0")

            item['url'] = response.url
            item['site'] = 'Big Latin Anal'
            item['parent'] = 'Big Latin Anal'
            item['network'] = 'Big Latin Anal'

            item['performers_data'] = self.get_performers_data(item['performers'])

            yield item

    def get_performers_data(self, performers):
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Big Latin Anal"
                perf['site'] = "Big Latin Anal"
                performers_data.append(perf)
        return performers_data
