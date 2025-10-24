import re
import json
import base64
import requests
import scrapy
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from tpdb.helpers.http import Http


class NetworkCzechVRSpider(BaseSceneScraper):
    name = 'CzechVRFS'
    network = 'Mental Pass'

    cfcookies = {}

    settings = get_project_settings()
    flare_address = settings.get('FLARE_ADDRESS')
    splash_address = settings.get('SPLASH_ADDRESS')

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    cookies = {
        'iagree': 'ano',
    }

    start_urls = [
        # ~ 'https://www.czechvr.com',
        # ~ 'https://www.czechvrcasting.com',
        # ~ 'https://www.czechvrfetish.com',
        # ~ 'https://www.vrintimacy.com'
    ]

    selector_map = {
        'title': '//div[contains(@class,"nazev")]/h1/span/following-sibling::text()|//div[contains(@class,"nazev")]/h2/span/following-sibling::text()',
        'description': '//div[@class="textDetail"]/text()',
        'date': '//article[@class="detail"]//div[contains(@class,"nazev")]/div[@class="datum"]/text()',
        'date_formats': ['%b %d %Y'],
        'image': '//article[@class="detail"]//div[@class="foto"]/dl8-video/@poster',
        'performers': '//article[@class="detail"]//div[contains(@class,"nazev")]/div[@class="featuring"]/a[contains(@href, "model")]/text()',
        'tags': '//div[@id="MoreTags"]//a/text()',
        'duration': '//div[@class="casDetail"]/span[1]/text()',
        'trailer': '//article[@class="detail"]//div[@class="foto"]/dl8-video/source/@src',
        'external_id': r'detail-(\d+)-',
        'pagination': '/vr-porn-videos?&next=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        for link in self.start_urls:
            url = self.get_next_page_url(link, self.page, link)
            headers = self.headers
            headers['Content-Type'] = 'application/json'
            setup = json.dumps({'cmd': 'sessions.create', 'session': 'czechvr'})
            requests.post(self.flare_address, data=setup, headers=headers)
            my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'czechvr', 'cookies': [{'name': 'mypage', 'value': str(self.page), 'domain': 'czechvr.com', 'link': link, 'iagree': 'ano'}]}
            yield scrapy.Request(self.flare_address, method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        jsondata = json.loads(response.body)
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        cookies = jsondata['solution']['cookies']
        self.cookies = cookies
        self.headers['User-Agent'] = jsondata['solution']['userAgent']
        for cookie in cookies:
            self.cfcookies[cookie['name']] = cookie['value']
            if cookie['name'] == 'mypage':
                page = int(cookie['value'])
        self.cfcookies['iagree'] = 'ano'
        link = jsondata['solution']['url']
        # ~ print(self.cookies)

        scenes = self.get_scenes(response, link)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if page and page < self.limit_pages:
                page = page + 1
                print('NEXT PAGE: ' + str(page))
                headers = self.headers
                headers['Content-Type'] = 'application/json'
                url = self.get_next_page_url(link, page, link)
                page = str(page)
                # ~ my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'cookies': [{'name': 'mypage', 'value': page, 'iagree': 'ano'}]}
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'cookies': [{'name': 'mypage', 'value': page}]}
                yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, link):
        pagination = "/vr-porn-videos"

        if page == 1:
            link = self.format_url(link, pagination)
        else:
            page = str(((int(page) - 1) * 15) + 1)
            link = self.format_url(link, f"{pagination}?&next={page}")
        return link

    def get_scenes(self, response, link):
        headers = self.headers
        scenes = response.xpath('//div[@class="nazev"]/h2/a/@href').getall()
        self.cookies.append({'name': 'iagree', 'value': 'ano'})
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                if scene[0] == '.':
                    scene = scene[1:]
                url = self.format_url(link, scene)
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url}
                yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse_my_scene, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Vr" not in tags and "VR" not in tags and "Virtual Reality" not in tags:
            tags.append("Virtual Reality")
        return tags

    def get_trailer(self, response):
        trailer = response.xpath('//article[@class="detail"]//div[@class="foto"]/dl8-video/source/@src').getall()
        if len(trailer) > 1:
            trailer.sort(reverse=True)
            trailer = trailer[0]
        if isinstance(trailer, list):
            trailer = trailer[0]
        return trailer

    def get_image(self, response):
        image = response.xpath('//article[@class="detail"]//div[@class="foto"]/dl8-video/@poster').get()
        if "/./" in image:
            image = image.replace("/./", "/")
        image = "https://www.czechvr.com" + image
        return image

    def get_title(self, response):
        # ~ print(response)
        title = response.xpath('//div[contains(@class,"nazev")]/h1/span/following-sibling::text()|//div[contains(@class,"nazev")]/h2/span/following-sibling::text()')
        if len(title) > 1:
            title = " ".join(title.getall())
            title = title.replace("  ", " ")
        else:
            title = title.get()
        return self.cleanup_title(title)

    def parse_my_scene(self, response):
        jsondata = json.loads(response.body)
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        item = SceneItem()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = "CzechVR"
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob(item['image'])
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['url'] = jsondata['solution']['url']
        item['id'] = re.search(r'detail-(\d+)-', item['url']).group(1)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['network'] = "Mental Pass"
        item['parent'] = "CzechVR"
        item['type'] = 'Scene'
        yield self.check_item(item, self.days)

    def get_image_blob(self, image):
        if image:
            req = Http.get(image)
            if req and req.ok:
                return base64.b64encode(req.content).decode('utf-8')
        return None
