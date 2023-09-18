import re
import urllib.parse
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkModelMediaSpider(BaseSceneScraper):
    name = 'ModelMedia'
    network = 'Model Media'

    start_urls = [
        'https://www.delphinefilms.com',
        'https://www.modelmediaasia.com',
        'https://www.jerkaoke.com',
    ]

    selector_map = {
        'external_id': r'trailers/(.*)',
        'pagination': '/videos?sort=published_at&page=%s'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            meta['link'] = link
            yield scrapy.Request(link, callback=self.start_delphine_1, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_delphine_1(self, response):
        meta = response.meta
        csrf_token = response.xpath('//meta[@name="csrf-token"]/@content').get()
        headers = {
            'Accept-Language': 'en-US,en',
            'x-requested-with': 'XMLHttpRequest',
            'x-csrf-token': csrf_token
        }
        for link in self.start_urls:
            yield scrapy.Request(f"{meta['link']}/adult_confirmation_and_accept_cookie", method="POST", callback=self.start_delphine_2, meta=meta, headers=headers, cookies=self.cookies)

    def start_delphine_2(self, response):
        meta = response.meta
        link = meta['link']
        yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "mus-reveal-video-widget")]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = scene.xpath('./div[contains(@class, "video-card")]/div/a[contains(@href, "/models/")]/span/text()').getall()
            title = scene.xpath('./a/@title').get()
            item['title'] = self.cleanup_title(title)
            item['description'] = ''

            item['image'] = scene.xpath('./a/div/img/@src').get()
            if not item['image']:
                item['image'] = None
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            trailer = scene.xpath('./a/@data-video-src')
            if trailer:
                item['trailer'] = trailer.get()
            else:
                item['trailer'] = ''
            item['url'] = scene.xpath('./a/@href').get()
            if not item['performers'] and "models_name=" in item['url']:
                performerlink = urllib.parse.unquote(item['url'])
                performerlink = re.search(r'models_name=(.*)', performerlink)
                if performerlink:
                    item['performers'] = performerlink.group(1).split(",")
            item['id'] = re.search(r'(?:trailers|plans)/(.*?)\?', item['url']).group(1)
            item['date'] = ''
            if "delphine" in response.url:
                item['site'] = "Delphine Films"
                item['parent'] = "Delphine Films"
            if "jerkaoke" in response.url:
                item['site'] = "Jerkaoke"
                item['parent'] = "Jerkaoke"
            if "modelmedia" in response.url:
                item['site'] = "Model Media Asia"
                item['parent'] = "Model Media Asia"
            item['network'] = "Model Media"
            item['tags'] = []
            item['duration'] = self.duration_to_seconds(scene.xpath('.//div[@class="timestamp"]/text()').get().strip())

            yield item
