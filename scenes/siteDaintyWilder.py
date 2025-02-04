import re
from requests import get
from cleantext import clean
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDaintyWilderSpider(BaseSceneScraper):
    name = 'DaintyWilder'

    start_urls = [
        'https://videos.daintywilder.com/'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "single-video")]/div[@class="video--info"]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h2/text()')
            if title:
                title = title.get()
                title = clean(title, no_emoji=True)
                item['title'] = self.cleanup_title(title)

            description = scene.xpath('.//h2/following-sibling::p[1]/text()')
            if description:
                description = description.get()
                description = clean(description, no_emoji=True)
                item['description'] = self.cleanup_description(description)

            image = scene.xpath('.//noscript/img/@src')
            if image:
                image = image.get()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)

                sceneid = re.search(r'static/(.*?)/', image)
                if sceneid:
                    item['id'] = sceneid.group(1)

            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', image)
            if scenedate:
                item['date'] = scenedate.group(1)
            else:
                item['date'] = ""

            item['performers'] = ['Dainty Wilder']

            item['site'] = "DaintyWilder"
            item['parent'] = "DaintyWilder"
            item['network'] = "DaintyWilder"

            item['type'] = 'Scene'
            item['url'] = response.url

            yield item
