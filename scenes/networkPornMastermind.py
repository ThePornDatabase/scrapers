import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornMastermindSpider(BaseSceneScraper):
    name = 'PornMastermind'

    start_urls = [
        ['https://pornmastermind.com', "Epic Sex", "/tour/epicsex/index.php?page=%s", "https://pornmastermind.com/tour/epicsex/"],
        # ~ ['https://pornmastermind.com', "Bangable", "/tour/bangable/index.php?page=%s", "https://pornmastermind.com/tour/bangable/"],
    ]

    selector_map = {
        'date': '//td[@class="date"]/text()',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[contains(@id, "bzone")]/following-sibling::table[1]//img[contains(@src, "002")]/@src',
        'performers': '//td[contains(text(), "Featuring")]/following-sibling::td[1]//a[contains(@class, "model_category_link")]/text()',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for site in self.start_urls:
            link = site[0]
            meta['site'] = site[1]
            meta['prefix'] = site[3]
            meta['parent'] = "Porn Mastermind"
            meta['network'] = "Porn Mastermind"
            singleurl = self.settings.get('url')
            if singleurl:
                yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
            else:
                meta['pagination'] = site[2]
                yield scrapy.Request(url=self.get_next_page_url(link, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "thumb")]')
        for scene in scenes:
            title = scene.xpath('./p/a[contains(@href, "?id=")]/following-sibling::strong[1]/text()|./p/strong/a[contains(@href, "?id=")]/text()').getall()
            title = "".join(title).strip()
            if not title:
                title = "Title Unavailable"
            meta['title'] = self.cleanup_title(title)
            meta['url'] = meta['prefix'] + scene.xpath('./p[1]/a[contains(@href, "?id=")]/@href').get()
            image = scene.xpath('.//img[contains(@class, "stdimage")]/@src')
            if image and "bangable" not in meta['site'].lower():
                image = "https://pornmastermind.com" + image.get()
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)
            if "&nats=" in meta['url']:
                meta['url'] = re.search(r'(.*)\&nats=', meta['url']).group(1)
            meta['id'] = re.search(r'id=(\d+)', meta['url']).group(1)
            if meta['id']:
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.xpath('//script[contains(text(), "img_video")]/text()')
            if image:
                image = image.get()
                image = re.search(r'\.src.*?[\'\"](.*)[\'\"]', image)
                if image:
                    image = self.format_link(response, image.group(1))
                    return image

        if not image or image in response.url:
            image = ""
        return image
