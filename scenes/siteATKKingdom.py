import re
from datetime import date, timedelta
import json
import base64
import requests
import scrapy
from scrapy.http import HtmlResponse

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ATKKingdomSpider(BaseSceneScraper):
    name = 'ATKKingdom'

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    start_urls = [
        'https://www.atkexotics.com',
        'https://www.atkarchives.com',
        'https://www.atkpetites.com',
        'https://www.amkingdom.com',
        'https://www.atkhairy.com',
        'https://www.atkpremium.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//b[contains(text(), "Description:")]/following-sibling::text()[1]|//span[@class="description"]/following-sibling::text()|//span[@class="description"]/following-sibling::span/text()',
        'date': '',
        'image': '//div[contains(@style, "background-image")]/@style',
        'image_blob': '//div[contains(@style, "background-image")]/@style',
        're_image': r'(https.*)\'',
        'performers': '',
        'tags': '//b[contains(text(), "Tags:")]/following-sibling::text()[1]|//span[@class="tags"]/following-sibling::text()',
        'external_id': r'model/(.*?)/',
        'trailer': '',
        'pagination': '/tour/movies/%s'
    }

    def start_requests(self):
        page = self.page
        for link in self.start_urls:
            if page > 1:
                url = link + "/tour/movies/" + str(page)
            else:
                url = link + "/tour/movies"
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
        indexdata = {}
        indexdata['response'] = response
        indexdata['url'] = jsondata['solution']['url']
        scenes = self.get_scenes(indexdata)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if page and page < self.limit_pages and page < 15:
                page = page + 1
                headers = self.headers
                headers['Content-Type'] = 'application/json'
                url = jsondata['solution']['url']
                if page > 1:
                    url = re.search(r'/(.*/)', url).group(1)
                url = self.get_next_page_url(url, page)
                print(f'Next Page URL: {url}')
                page = str(page)
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'cookies': [{'name': 'mypage', 'value': page}]}
                yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_scenes(self, indexdata):
        response = indexdata['response']
        response_url = indexdata['url']
        if "atkarchives" in response_url or "atkpetites" in response_url or "atkhairy" in response_url or "atkpremium" in response_url:
            scenes = response.xpath('//div[contains(@class, "tourMovieContainer")]')
        if "atkexotics" in response_url or "amkingdom" in response_url:
            scenes = response.xpath('//div[contains(@class, "movie-wrap")]')
        for scene in scenes:
            if "atkarchives" in response_url or "atkpetites" in response_url or "atkhairy" in response_url or "atkpremium" in response_url:
                link = scene.xpath('.//div[@class="player"]/a/@href').get()
                scenedate = scene.xpath('.//span[contains(@class, "movie_date")]/text()').get()
                if scenedate:
                    scenedate = self.parse_date(scenedate.strip()).isoformat()
                else:
                    scenedate = self.parse_date('today').isoformat()
                performer = scene.xpath('./div/span[contains(@class,"video_name")]/a/text()').get()
                performer = performer.strip()
                if not performer:
                    performer = ''
            if "atkexotics" in response_url or "amkingdom" in response_url:
                link = scene.xpath('./div[@class="movie-image"]/a/@href').get()
                scenedate = scene.xpath('./div[@class="date left clear"][2]/text()').get()
                if scenedate:
                    scenedate = self.parse_date(scenedate.strip()).isoformat()
                else:
                    scenedate = self.parse_date('today').isoformat()
                performer = scene.xpath('./div[@class="video-name"]/a/text()').get()
                performer = performer.strip()
                if not performer:
                    performer = ''

            if link:
                if "atkarchives" in response_url:
                    link = "https://www.atkarchives.com" + link
                if "atkexotics" in response_url:
                    link = "https://www.atkexotics.com" + link
                if "atkpremium" in response_url:
                    link = "https://www.atkpremium.com" + link
                if "atkpetites" in response_url:
                    link = "https://www.atkpetites.com" + link
                if "atkhairy" in response_url:
                    link = "https://www.atkhairy.com" + link
                if "amkingdom" in response_url:
                    link = "https://www.amkingdom.com" + link

                headers = self.headers
                headers['Content-Type'] = 'application/json'
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': link, 'cookies': [{'name': 'mydate', 'value': scenedate}, {'name': 'performer', 'value': performer}]}
                if "?w=" not in link:
                    yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse_scene, body=json.dumps(my_data), headers=headers, cookies=self.cookies)
                else:
                    item = SceneItem()
                    item['network'] = "ATK Girlfriends"
                    if "atkarchives" in response_url:
                        item['parent'] = "ATK Archives"
                        item['site'] = "ATK Archives"
                    if "atkexotics" in response_url:
                        item['parent'] = "ATK Exotics"
                        item['site'] = "ATK Exotics"
                    if "atkpremium" in response_url:
                        item['parent'] = "ATK Premium"
                        item['site'] = "ATK Premium"
                    if "atkpetites" in response_url:
                        item['parent'] = "ATK Petites"
                        item['site'] = "ATK Petites"
                    if "atkhairy" in response_url:
                        item['parent'] = "ATK Hairy"
                        item['site'] = "ATK Hairy"
                    if "amkingdom" in response_url:
                        item['parent'] = "ATK Galleria"
                        item['site'] = "ATK Galleria"
                    title = scene.xpath('.//img/@alt')
                    if title:
                        item['title'] = self.cleanup_title(title.get())
                    else:
                        item['title'] = ''
                    item['date'] = scenedate
                    item['url'] = response_url
                    image = scene.xpath('.//img/@src')
                    if image:
                        item['image'] = image.get().strip()
                    else:
                        item['image'] = ''
                    if item['image']:
                        item['image_blob'] = base64.b64encode(requests.get(item['image']).content).decode('utf-8')
                    performer = scene.xpath('./div[@class="video-name"]/a/text()')
                    if performer:
                        item['performers'] = [performer.get().strip()]
                    else:
                        item['performers'] = []
                    item['description'] = None
                    item['trailer'] = None
                    item['tags'] = []
                    if item['image']:
                        item['id'] = re.search(r'.*/(\d{4,8})/.*', item['image']).group(1)

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
        if base[0:1] == "/":
            base = "https:/" + base
        url = base + str(page)
        return url

    def parse_scene(self, response):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        response_url = jsondata['solution']['url']
        cookies = jsondata['solution']['cookies']
        for cookie in cookies:
            if cookie['name'] == 'mydate':
                scenedate = cookie['value']
            if cookie['name'] == 'performer':
                performer = cookie['value']
        item = SceneItem()
        if scenedate:
            item['date'] = self.parse_date(scenedate).isoformat()
        else:
            item['date'] = self.parse_date('today').isoformat()

        if performer:
            item['performers'] = [performer]
        else:
            item['performers'] = []

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob(response)
        item['tags'] = self.get_tags(response)
        if "" in item['tags']:
            item['tags'].remove("")
        item['id'] = re.search(r'/movie/(.*?)/', jsondata['solution']['url']).group(1)
        item['trailer'] = self.get_trailer(response)
        item['url'] = jsondata['solution']['url']
        item['network'] = "ATK Girlfriends"

        if "atkarchives" in response_url:
            item['parent'] = "ATK Archives"
            item['site'] = "ATK Archives"
        if "atkexotics" in response_url:
            item['parent'] = "ATK Exotics"
            item['site'] = "ATK Exotics"
        if "atkpremium" in response_url:
            item['parent'] = "ATK Premium"
            item['site'] = "ATK Premium"
        if "atkpetites" in response_url:
            item['parent'] = "ATK Petites"
            item['site'] = "ATK Petites"
        if "atkhairy" in response_url:
            item['parent'] = "ATK Hairy"
            item['site'] = "ATK Hairy"
        if "amkingdom" in response_url:
            item['parent'] = "ATK Galleria"
            item['site'] = "ATK Galleria"

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
            image = None
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
        return None
