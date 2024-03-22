import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSlimeWaveSpider(BaseSceneScraper):
    name = 'SlimeWave'
    network = 'SlimeWave'
    parent = 'SlimeWave'
    site = 'SlimeWave'

    selector_map = {
        'title': '//h1[@class="title--3"]/text()',
        'description': '//div[contains(@class,"accordion__content")]/h5/following-sibling::p//text()',
        'date': '//div[contains(@class,"accordion__content")]//td[contains(text(), "Date added")]/following-sibling::td/text()',
        'date_formats': ['%d %B %Y'],
        'image': '//div[contains(@class,"show---link")]/img/@src',
        'performers': '//figcaption[contains(@class,"girls-item--content")]/h4/text()',
        'trailer': '',
        'external_id': r'movie/(\d+)/',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        # Deprecated in favor of Tainster scraper
        # ~ link = "https://www.sinx.com/channel/Slime-Wave/all"
        # ~ yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        links = response.xpath('//a[@class="item--link"]/@href').getall()
        for link in links:
            meta['pagination'] = link + "?page=%s"
            yield scrapy.Request(url=self.get_next_page_url("https://www.sinx.com/", self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video_item--player"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"accordion__content")]//td[contains(text(), "Runtime")]/following-sibling::td/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None

    def get_tags(self, response):
        taglist = response.xpath('//div[contains(@class,"video-page--tag")]//a/span/text()').getall()
        tags = []
        for tag in taglist:
            tag = tag.replace("#", "")
            tag = re.sub(r"([A-Z])", r" \1", tag)
            tags.append(tag)
        return tags
