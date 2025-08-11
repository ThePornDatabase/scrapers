import re
from requests import get
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBigTitsLatinaAssSpider(BaseSceneScraper):
    name = 'BigTitsLatinaAss'
    network = 'Big Tits Latina Ass'
    parent = 'Big Tits Latina Ass'
    site = 'Big Tits Latina Ass'

    start_urls = [
        'https://www.bigtitslatinass.com/home.htm',
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
        scenes = response.xpath('//table/tbody[1]//div[@align="center" and contains(text(), "Model:")]/text()/ancestor::tbody[1]')
        for scene in scenes:
            item = self.init_scene()

            performer = scene.xpath('.//div[@align="center" and contains(text(), "Model")]/text()')
            performer = re.sub(r'[^A-Za-z: ]+', '', performer.get())
            item['performers'] = [performer.replace("Model:", "").strip()]

            title = scene.xpath('.//div[@align="center" and contains(text(), "Model")]/strong/text()[1]').get()
            title = re.sub(r'[^A-Za-z -]+', '', title)
            search_title = re.search(r'- (.*)-', title)
            if not search_title:
                search_title = re.search(r'- (.*)', title)
            if search_title:
                item['title'] = search_title.group(1)
            else:
                item['title'] = title
            item['title'] = string.capwords(item['title'])

            image = scene.xpath('./tr[1]/td[1]//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'(\d+)\.', item['image']).group(1).lstrip("0")

            duration = scene.xpath('.//div[@align="right" and contains(text(), "Min")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    duration = duration.group(1)
                    item['duration'] = self.duration_to_seconds(duration)
            item['url'] = response.url
            item['site'] = 'Big Tits Latina Ass'
            item['parent'] = 'Big Tits Latina Ass'
            item['network'] = 'Big Tits Latina Ass'

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
                perf['network'] = "Big Tits Latina Ass"
                perf['site'] = "Big Tits Latina Ass"
                performers_data.append(perf)
        return performers_data
