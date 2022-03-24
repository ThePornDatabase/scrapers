import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy import Selector


class SitePJGirlsSpider(BaseSceneScraper):
    name = 'PJGirls'
    network = 'PJGirls'
    parent = 'PJGirls'
    site = 'PJGirls'

    start_urls = [
        'https://www.pjgirls.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '//div[@class="info"]/h3[1]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="thumbs clear nomargin"]/div[@class="thumb mini"]/a/@href',
        'image_blob': True,
        'performers': '//div[@class="info"]/h3/a[contains(@href, "model")]/text()',
        'tags': '//div[contains(@class, "detailTagy")]/a/text()',
        'external_id': r'video/(\d+)',
        'trailer': '',
        'pagination': '/en/videos/?order=date&page=%s'
    }

    def start_requests(self):
        start_page = "https://www.pjgirls.com/en/videos/?order=date"
        start_page = requests.get(start_page)
        if start_page:
            sel = Selector(text=start_page.content)
            next_page = sel.xpath('//a[@title="next page"][1]/@href')
            if next_page:
                curr_page = re.search(r'page=(\d+)', next_page.get())
                if curr_page:
                    curr_page = int(curr_page.group(1)) + 1

        page = curr_page - (self.page - 1)

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, page),
                                 callback=self.parse,
                                 meta={'page': page, 'start_page': curr_page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and (response.meta['start_page'] - response.meta['page']) < self.limit_pages and response.meta['page'] > 1:
                meta = response.meta
                meta['page'] = meta['page'] - 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb video"]/a[@class="img"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = super().get_title(response)
        title = title.lower().replace("video:", "").strip()
        return string.capwords(title)
