import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMegaBootyLatinAssSpider(BaseSceneScraper):
    name = 'MegaBootyLatinAss'
    network = 'Mega Booty Latin Ass'
    parent = 'Mega Booty Latin Ass'
    site = 'Mega Booty Latin Ass'

    start_urls = [
        'https://www.megabootylatinass.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/home%s.htm',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://www.megabootylatinass.com/home.htm"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(text(), "Model:")]/ancestor::tbody[1]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//div[@align="center"]/strong/text()').get()
            title = title.replace("&amp;", "&")
            title = re.sub(r'[^A-Za-z: -!&]+', '', title)
            item['title'] = string.capwords(title)

            performer = scene.xpath('.//div[@align="center"]/text()[contains(., "Model:")][1]')
            if performer:
                performer = performer.get()
                performer = re.sub(r'[^A-Za-z: ]+', '', performer)
                performer = performer.replace("Model:", "").strip()
                item['performers'] = [string.capwords(performer)]

            duration = scene.xpath('.//div[@align="right" and contains(text(), "Min")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    duration = duration.group(1)
                    item['duration'] = self.duration_to_seconds(duration)

            image = scene.xpath('./tr[1]/td[1]//img/@src').get()
            item['image'] = self.format_link(response, image)
            # ~ item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = re.search(r'.*/(.*?)\.', item['image']).group(1).lstrip("0")

            item['url'] = response.url
            item['site'] = 'Mega Booty Latin Ass'
            item['parent'] = 'Mega Booty Latin Ass'
            item['network'] = 'Mega Booty Latin Ass'

            item['performers_data'] = self.get_performers_data(item['performers'])
            # ~ print(item)
            yield item

    def get_performers_data(self, performers):
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Mega Booty Latin Ass"
                perf['site'] = "Mega Booty Latin Ass"
                performers_data.append(perf)
        return performers_data
