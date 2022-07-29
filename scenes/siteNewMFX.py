import re
import base64
import requests
import scrapy
from scrapy.http import FormRequest
from scrapy.utils.project import get_project_settings
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNewMFXSpider(BaseSceneScraper):
    name = 'NewMFX'
    network = 'New MFX'
    parent = 'New MFX'
    site = 'New MFX'

    start_urls = [
        'https://newmfx.com',
    ]

    headers = {
        'host': 'newmfx.com',
        'referer': 'https://newmfx.com/latest-videos?page=3',
        'cookie': '_clck=td4lmq|1|f39|0; XSRF-TOKEN=eyJpdiI6IjI5VktTTFVtQWRLWUgyc3pNMUNZRFE9PSIsInZhbHVlIjoibDJDb3RCNkxXcGR1OWUzcG5JOG40VG43US9VK28xNHJtWjRERTJrNzZZM2dZbnR3bGhPcDJxNXhLSzZJQVo0T3A3dS9Dcks4NDZxWE44UzdubTE1UXhDcTlSb2phOWhTdEJmWFpGSWlMSnFFVGZ3a0Mvc1BWdlBmRjdyRTBReHYiLCJtYWMiOiI1ZDhjMjIzZjg5NTkyYTdkM2ViYmYzZTBkMDI2MGNiMzg4NWZlNTNlMzI0NzMzMmUzZWJjZWMyNmEzY2YyM2E4IiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6IjN2N3BpL3kyUlNMenppcTNFRTVwY0E9PSIsInZhbHVlIjoiaGtGclE0VWlVZlZtNFgxdmZBY2RDV2NqZ3F6YXROeWRZRDM4ZTdHVnpXRGo2WklnTXg4bEUzV3VJV3pJb0lFTmxuaG8wazZ5Vk5ISk9nUnIzZTFSWEJUWklEWUJpZmFlbkxMeitGZERQb3h6WWZHRFVrT0pmdVdFb2tlUVhMa1QiLCJtYWMiOiI0OGNiNjUwY2U2OGMxYTI5NjdjZWI3ZGY1Mjg1Y2Y5ZmE0YWU1Njk0MWI4YTkxMWEwZDI1NDllNTUyNTQ5MDI5IiwidGFnIjoiIn0%3D; _clsk=erukl|1658121750401|7|1|l.clarity.ms/collect',
    }

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="container"]/h2[contains(text(), "Description")]/following-sibling::p//text()',
        'date': '//div[contains(@class, "date")]/span[contains(text(), ",")]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@class="thumb-movie"]/a/@href',
        'performers': '//span[@class="subtitle"]/a/text()',
        'tags': '//div[contains(@class, "category")]/a/span[@class="info"]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/latest-videos?page=%s'
    }

    def start_requests(self):
        link = "https://newmfx.com/"
        yield FormRequest(url=link, callback=self.start_requests_login, cookies=self.cookies)

    def start_requests_login(self, response):
        csrf = response.xpath('//form/input/@value')
        if csrf:
            csrf = csrf.get().strip()

            frmdata = {}
            frmdata['_token'] = csrf
            url = "https://newmfx.com"
            yield FormRequest(url, formdata=frmdata, callback=self.start_requests_actual, cookies=self.cookies)

    def start_requests_actual(self, response):
        settings = get_project_settings()

        meta = {}
        meta['page'] = self.page
        if 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-list-video"]')
        for scene in scenes:
            image = scene.xpath('./a/img/@src')
            if image:
                sceneid = re.search(r'images/(.*?)/', image.get())
                if sceneid:
                    meta['id'] = sceneid.group(1).strip()

            scenedate = scene.xpath('.//span[@class="date-video"]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get().strip(), date_formats=['%b %d, %Y']).isoformat()

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) or 'id' in meta:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image_blob_from_link(self, image):

        header_dict = {'Referer': 'https://newmfx.com'}
        if image:
            return base64.b64encode(requests.get(image, headers=header_dict).content).decode('utf-8')
        return None
