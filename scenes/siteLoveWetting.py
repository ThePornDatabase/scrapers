import re
import scrapy
import requests
from datetime import date, timedelta
import string

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLoveWettingSpider(BaseSceneScraper):
    name = 'LoveWetting'

    cookies = [{"name": "cookie_mastercard", "value": "1"}]

    start_url = 'https://www.lovewetting.com'

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/wetting-desperation-videos.html?order=date&page=%s'
    }

    def get_next_page_url(self, base, page, max_pages):
        page = max_pages - int(page)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        link = "https://www.lovewetting.com/wetting-desperation-videos.html"
        yield scrapy.Request(link, callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta

        page_limit = response.xpath('//div[contains(@class, "paging-top")]//select[@id="select_page2"]/option[@selected]/text()')
        if page_limit:
            page_limit = page_limit.get()
            max_pages = re.search(r'(\d+)', page_limit).group(1)
            meta['max_pages'] = int(max_pages) + 1
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['max_pages']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['max_pages']), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item"]')
        print(f'Found {len(scenes)} Scenes')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./div[@class="box-info"]/h3/text()')
            item['title'] = ''
            if title:
                item['title'] = self.cleanup_title(title.get())

            description = scene.xpath('./div[@class="box-info"]/article/div[contains(@class, "description")]/text()')
            item['description'] = ''
            if description:
                item['description'] = self.cleanup_description(description.get())

            scenedate = scene.xpath('./div[@class="box-info"]/p/span/i[contains(@class, "calendar")]/following-sibling::text()')
            item['date'] = self.parse_date('today').isoformat()
            item['date'] = ''
            if scenedate:
                item['date'] = self.parse_date(scenedate.get().strip()).isoformat()

            image = scene.xpath('.//div[@class="imgwrap"]//img/@src')
            item['image'] = None
            item['id'] = ''
            item['url'] = ''
            if image:
                image = image.get()
                image = image.strip().replace("&amp;", "&")
                item['image'] = self.format_link(response, image)
                item['id'] = re.search(r'\d{4}\/(.*)\&', image).group(1)
                item['url'] = self.format_link(response, re.search(r'(.*\d{4}\/.*)\&', image).group(1))

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            performers = scene.xpath('.//p[@class="tags"]/strong[contains(text(), "Models")]/following-sibling::a/text()')
            item['performers'] = []
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers.getall()))

            tags = scene.xpath('.//p[@class="tags"]/strong[contains(text(), "Tags")]/following-sibling::a/text()')
            item['tags'] = []
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.getall()))

            item['site'] = "Love Wetting"
            item['parent'] = "Love Wetting"
            item['network'] = "Love Wetting"
            item['trailer'] = ''

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
