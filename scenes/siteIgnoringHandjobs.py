import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteIgnoringHandjobsSpider(BaseSceneScraper):
    name = 'IgnoringHandjobs'
    network = 'IgnoringHandjobs'
    parent = 'IgnoringHandjobs'
    site = 'IgnoringHandjobs'

    selector_map = {
        'title': '//span[@itemprop="item"]/span[@itemprop="name"]/text()',
        'description': '',
        'date': '//meta[@property="article:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[contains(@class, "entry-content")]/div[1]/div[1]/h1[1]/a[1]/img[1]/@data-src',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        start_url = "https://www.ignoringhandjobs.com/updates/"
        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            yield scrapy.Request(start_url, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[contains(@class, "rpwe-li")]')
        for scene in scenes:
            scenedate = scene.xpath('.//time[contains(@class, "published")]/@datetime').get()
            meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
            meta['orig_image'] = scene.xpath('.//img/@data-src').get()
            if not meta['date']:
                image = re.search(r'(\d{4}/\d{2})', meta['orig_image']).group(1)
                meta['date'] = image.replace('/', '-') + "-01"
            else:
                meta['date'] = meta['date'].group(1)
            scene = scene.xpath('./a[1]/@href').get()
            meta['id'] = re.search(r'.*/(.*?)/', scene).group(1)
            scenedate = None
            if self.check_item(meta, self.days):
                if meta['id']:
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ["Handjob"]

    def get_id(self, response):
        meta = response.meta
        if "id" in meta and meta['id']:
            return meta['id']
        sceneid = re.search(r'.*/(.*?)/', response.url).group(1)
        return sceneid

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if not image or image in response.url:
            image = meta['orig_image']
        return image
