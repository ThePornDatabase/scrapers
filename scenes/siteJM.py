#  Requires Flaresolverr for base page retrieval (https://github.com/FlareSolverr/FlareSolverr)
#  Please enter fields into settings.py with full command such as:
#  FLARE_ADDRESS = 'http://192.168.1.151:8191/v1'

import re
from datetime import date, timedelta
import json
import base64
import requests
import scrapy
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteJacquieEtMichelTVSpider(BaseSceneScraper):
    name = 'Jacquie'
    network = "Jacquie et Michel TV"
    parent = "Jacquie et Michel TV"

    cfcookies = {}

    settings = get_project_settings()
    flare_address = settings.get('FLARE_ADDRESS')

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    start_urls = [
        'https://www.jacquieetmicheltv.net',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '',
        'external_id': r'/en/content/([0-9a-f]{16,})/',
        'trailer': '',
        'pagination': '/en/content/list?page=%s'
    }

    # The tour was rebuilt.  /en/videos/pageN.html redirects to /en/content/list,
    # div.video-list and a.video-item__thumb are gone, and scene ids are 24-character
    # hex strings rather than digits.  Every card is a <content-card> element whose
    # mpe attribute carries a base64 JSON payload holding the title, release date,
    # runtime, cast and tags, so those come off the listing; the scene page is still
    # visited for the full-size still and the synopsis.  Splash is no longer needed
    # -- SPLASH_ADDRESS is commented out in settings and the stills fetch directly.

    async def start(self):
        if hasattr(self, 'start_page'):
            page = self.start_page
        else:
            page = self.page
        page = int(page)
        url = "https://www.jacquieetmicheltv.net/en/content/list?page=%s" % page

        headers = self.headers
        headers['Content-Type'] = 'application/json'
        setup = json.dumps({'cmd': 'sessions.create', 'session': 'jacquie'})
        requests.post(self.flare_address, data=setup, headers=headers)
        my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'jacquie', 'cookies': [{'name': 'mypage', 'value': str(self.page)}]}
        yield scrapy.Request(self.flare_address, method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        cookies = jsondata['solution']['cookies']
        self.cookies = cookies
        self.headers['User-Agent'] = jsondata['solution']['userAgent']
        for cookie in cookies:
            self.cfcookies[cookie['name']] = cookie['value']
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

        if count or page < 180:
            if page and page < self.limit_pages:
                page = page + 1
                headers = self.headers
                headers['Content-Type'] = 'application/json'
                url = jsondata['solution']['url']
                url = self.get_next_page_url(url, page)
                print(f'Next Page URL: {url}')
                page = str(page)
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'jacquie', 'cookies': [{'name': 'mypage', 'value': page}]}
                yield scrapy.Request(self.flare_address, method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_scenes(self, indexdata):
        response = indexdata['response']
        headers = self.headers
        headers['Content-Type'] = 'application/json'
        for card in response.xpath('//content-card'):
            link = card.xpath('.//a[contains(@href, "/en/content/")]/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = {'id': re.search(self.get_selector_map('external_id'), link).group(1)}
            meta.update(self.decode_card(card))

            my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'session': 'jacquie',
                       'url': "https://www.jacquieetmicheltv.net" + link}
            yield scrapy.Request(self.flare_address, method='POST', callback=self.parse_scene,
                                 body=json.dumps(my_data), headers=headers, cookies=self.cookies, meta=meta)

    @staticmethod
    def decode_card(card):
        """The card's mpe attribute holds a base64 JSON blob with the facts the
        rebuilt markup no longer exposes as elements."""
        mpe = card.xpath('.//a[contains(@href, "/en/content/")]/@mpe').get() or ''
        payload = re.search(r"'([A-Za-z0-9+/=]{40,})'", mpe)
        if not payload:
            return {}
        try:
            data = json.loads(base64.b64decode(payload.group(1)))
        except Exception:
            return {}

        out = {}
        if data.get('contentTitle'):
            out['title'] = data['contentTitle']
        published = re.search(r'(\d{4}-\d{2}-\d{2})', data.get('contentPublicationDate') or '')
        if published:
            out['date'] = published.group(1)
        if data.get('contentDuration'):
            out['duration'] = str(int(data['contentDuration']))
        actors = [x.strip() for x in (data.get('contentActorsNames') or '').split(',') if x.strip()]
        out['performers'] = list(dict.fromkeys(actors))
        tags = [x.strip().title() for x in (data.get('contentTagsNames') or '').split(',') if x.strip()]
        out['tags'] = list(dict.fromkeys(tags))
        return out

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                return list(map(lambda x: x.replace(",", "").strip().title(), tags.getall()))
        return []

    def get_performers(self, response):
        return []

    def get_site(self, response):
        return "Jacquie et Michel TV"

    def parse_scene(self, response):
        meta = self.copy_meta(response)
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        page = HtmlResponse(url=jsondata['solution']['url'], body=htmlcode, encoding='utf-8')

        item = SceneItem()
        item['title'] = (meta.get('title')
                         or page.xpath('//h1/text()').get() or '').replace(" ...", "").strip()
        if not item['title']:
            return
        item['title'] = self.cleanup_title(item['title'])

        item['date'] = meta.get('date')
        item['duration'] = meta.get('duration')
        item['performers'] = meta.get('performers', [])
        item['tags'] = meta.get('tags', [])

        description = page.xpath('//meta[@property="og:description"]/@content').get() or ''
        item['description'] = self.cleanup_description(re.sub(r'\s+', ' ', description))

        item['image'] = (page.xpath(self.get_selector_map('image')).get() or '').strip()
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

        item['id'] = meta.get('id')
        item['trailer'] = ''
        item['url'] = jsondata['solution']['url']
        item['network'] = "Jacquie et Michel TV"
        item['parent'] = "Jacquie et Michel TV"
        item['site'] = "Jacquie et Michel TV"
        item['type'] = 'Scene'

        item = self.check_item(item, self.days)
        if item:
            yield item

    def closed(self, response):
        headers = self.headers
        headers['Content-Type'] = 'application/json'
        setup = json.dumps({'cmd': 'sessions.destroy', 'session': 'jacquie'})
        requests.post(self.flare_address, data=setup, headers=headers)
