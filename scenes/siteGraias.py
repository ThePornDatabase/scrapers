import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.http import FormRequest


class SiteGraiasSpider(BaseSceneScraper):
    name = 'Graias'
    network = 'Graias Studio'
    parent = 'Graias Studio'
    site = 'Graias Studio'

    start_urls = [
        'https://www.graias.com',
    ]

    custom_settings = {'DEBUG_COOKIES': 'True'}

    selector_map = {
        'title': '//div[contains(@class, "videofocim")]/h1[1]/text()',
        'description': '//div[@class="col-lg-7"]/p[1]/text()',
        'date': '//div[contains(@class, "videofocim")]/p/span[2]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="col-lg-7"]//a[contains(@href, "/slave/")]/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'duration': '//div[contains(@class, "videofocim")]/p/span[contains(text(), "minutes")]/text()',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(\d+)',
        'pagination': '/preview/%s',
        'type': 'Scene',
    }

    def start_requests(self):

        url = "https://www.graias.com/"
        yield scrapy.Request(url, callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        cookie_xsrf = response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(";")[0].split("=")
        cookie_laravel = response.headers.getlist('Set-Cookie')[1].decode("utf-8").split(";")[0].split("=")
        csrf = response.xpath('//input[@type="hidden" and @name="_token"]/@value')
        if csrf:
            csrf = csrf.get()
            frmheaders = {'laravel_session': cookie_laravel[1], 'XSRF-TOKEN': cookie_xsrf[1]}
            frmdata = {"_token": csrf, "siteAccepted": '1'}
            url = "https://www.graias.com/"
            yield FormRequest(url, headers=frmheaders, formdata=frmdata, callback=self.start_requests_actual, cookies=self.cookies)

    def start_requests_actual(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//button[contains(.//p, "Details")]/a/@href|//button[contains(.//p, "Reviews")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_tags(self, response):
        tags = response.xpath(self.get_selector_map('tags'))
        if tags:
            tags = tags.get()
            return list(map(lambda x: string.capwords(x.strip()), tags.split(",")))
        return []
