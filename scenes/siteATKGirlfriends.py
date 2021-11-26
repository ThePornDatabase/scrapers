import re
from datetime import date, timedelta
import json
import base64
import requests
import scrapy
from scrapy.http import HtmlResponse

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ATKGirlfriendsSpider(BaseSceneScraper):
    name = 'ATKGirlfriends'
    network = 'ATK Girlfriends'
    parent = 'ATK Girlfriends'

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    start_urls = [
        'https://www.atkgirlfriends.com',
    ]

    headers = {
        'referer': 'https://www.atkgirlfriends.com',
    }

    selector_map = {
        'title': '//title/text()',
        'description': '//b[contains(text(),"Description")]/following-sibling::text()[1]',
        'date': '',
        'image': '//div[contains(@style,"background")]/@style',
        'image_blob': '//div[contains(@style,"background")]/@style',
        're_image': r'url\(\'(http.*)\'\)',
        'performers': '//div[contains(@class,"model-profile-wrap")]/text()[1]',
        'tags': '//b[contains(text(),"Tags")]/following-sibling::text()',
        'external_id': r'/tour/.+?/(.*)?/',
        'trailer': '',
        'pagination': '/tour/movies/%s'
    }

    def start_requests(self):
        for link in self.start_urls:
            url = self.get_next_page_url(link, self.page)
            headers = self.headers
            headers['Content-Type'] = 'application/json'
            my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'cookies': [{'name': 'mypage', 'value': str(self.page)}]}
            yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        cookies = jsondata['solution']['cookies']
        for cookie in cookies:
            if cookie['name'] == 'mypage':
                page = int(cookie['value'])
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if page and page < self.limit_pages and page < 15:
                page = page + 1
                print('NEXT PAGE: ' + str(page))
                headers = self.headers
                headers['Content-Type'] = 'application/json'
                url = self.get_next_page_url("https://www.atkgirlfriends.com/tour/movies/", page)
                page = str(page)
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'cookies': [{'name': 'mypage', 'value': page}]}
                yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"movie-wrap")]')
        for scene in scenes:
            link = scene.xpath('./div[@class="movie-image"]/a/@href').get()
            link = "https://www.atkgirlfriends.com" + link
            scenedate = scene.xpath('./div[@class="vid-count left"]/text()').get()
            if scenedate:
                scenedate = self.parse_date(scenedate.strip()).isoformat()
            else:
                scenedate = self.parse_date('today').isoformat()
            if "join.atkgirlfriends.com" not in link:
                headers = self.headers
                headers['Content-Type'] = 'application/json'
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': link, 'cookies': [{'name': 'mydate', 'value': scenedate}]}
                yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse_scene, body=json.dumps(my_data), headers=headers, cookies=self.cookies)
            else:
                item = SceneItem()
                title = scene.xpath('./div/a/text()').get()
                if title:
                    item['title'] = self.cleanup_title(title)
                else:
                    item['title'] = ''

                if scenedate:
                    item['date'] = scenedate
                else:
                    item['date'] = self.parse_date('today').isoformat()

                image = scene.xpath('./div/a/img/@src').get()
                if image:
                    item['image'] = image.strip().replace("/sm_", "/")
                    item['image_blob'] = base64.b64encode(requests.get(item['image']).content).decode('utf-8')
                else:
                    item['image'] = None
                    item['image_blob'] = None

                url = scene.xpath('./div/a[contains(@href,"/model/")]/@href').get()
                if url:
                    item['url'] = "https://www.atkgirlfriends.com" + url.strip()
                else:
                    item['url'] = ''

                externalid = item['title'].replace(" ", "-").lower()
                externalid = re.sub('[^a-zA-Z0-9-]', '', externalid)
                item['id'] = externalid
                # ~ item['id'] = re.search(r'/model/(.*?)/', jsondata['solution']['url']).group(1)

                item['performers'] = []
                item['tags'] = []
                item['trailer'] = ''
                item['description'] = ''
                item['site'] = "ATK Girlfriends"
                item['parent'] = "ATK Girlfriends"
                item['network'] = "ATK Girlfriends"

                if item['title'] and item['image']:
                    days = int(self.days)
                    if days > 27375:
                        filterdate = "0000-00-00"
                    else:
                        filterdate = date.today() - timedelta(days)
                        filterdate = filterdate.strftime('%Y-%m-%d')

                    if self.debug:
                        if not item['date'] > filterdate:
                            item['filtered'] = "Scene filtered due to date restraint"
                        print(item)
                    else:
                        if filterdate:
                            if item['date'] > filterdate:
                                yield item
                        else:
                            yield item

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).get()
            if tags:
                tags = tags.split(",")

                tags2 = tags.copy()
                for tag in tags2:
                    matches = ['4k']
                    if any(x in tag.lower() for x in matches):
                        tags.remove(tag)

                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url

    def parse_scene(self, response):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        cookies = jsondata['solution']['cookies']
        for cookie in cookies:
            if cookie['name'] == 'mydate':
                scenedate = cookie['value']

        item = SceneItem()
        if scenedate:
            item['date'] = self.parse_date(scenedate).isoformat()
        else:
            item['date'] = self.parse_date('today').isoformat()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob(response)
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = re.search(r'/movie/(.*?)/', jsondata['solution']['url']).group(1)
        item['trailer'] = self.get_trailer(response)
        item['url'] = jsondata['solution']['url']
        item['network'] = "ATK Girlfriends"
        item['parent'] = "ATK Girlfriends"
        item['site'] = "ATK Girlfriends"

        days = int(self.days)
        if days > 27375:
            filterdate = "0000-00-00"
        else:
            filterdate = date.today() - timedelta(days)
            filterdate = filterdate.strftime('%Y-%m-%d')

        if self.debug:
            if not item['date'] > filterdate:
                item['filtered'] = "Scene filtered due to date restraint"
            print(item)
        else:
            if filterdate:
                if item['date'] > filterdate:
                    yield item
            else:
                yield item

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            imagealt = response.xpath('//div[contains(@style,"background")]/@style')
            if imagealt:
                imagealt = re.search(r'url\(\"(http.*)\"\)', imagealt.get())
                if imagealt:
                    imagealt = imagealt.group(1)
                    imagealt = self.format_link(response, imagealt)
                    return imagealt.replace(" ", "%20")
        return image

    def get_image_blob(self, response):
        image = super().get_image(response)
        if not image:
            imagealt = response.xpath('//div[contains(@style,"background")]/@style')
            if imagealt:
                imagealt = re.search(r'url\(\"(http.*)\"\)', imagealt.get())
                if imagealt:
                    imagealt = imagealt.group(1)
                    imagealt = self.format_link(response, imagealt)
                    image = imagealt.replace(" ", "%20")
        if image:
            return base64.b64encode(requests.get(image).content).decode('utf-8')
        return ''
