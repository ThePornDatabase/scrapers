import re
import string
import json
import scrapy
from datetime import datetime
from tpdb.BaseSceneScraper import BaseSceneScraper
from slugify import slugify
from tpdb.helpers.http import Http
import requests
true = True
false = False


class SiteBellesaHouseSpider(BaseSceneScraper):
    name = 'BellesaHouse'
    network = 'Bellesa'

    cookies = [
        {"domain": "bellesaplus.co", "name": "bellesa_agegate", "path": "/", "value": "true"},
    ]

    start_urls = [
        'https://www.bellesa.co',
        'https://bellesaplus.co',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': False,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        },
    }

    def get_next_page_url(self, base, page):
        if "bellesa.co" in base:
            pagination = "/api/rest/v1/videos?filter%5Bprovider%5D=or%3Abellesa-films%2Cbellesa-house%2Cbellesa-blind-date%2Czero-to-hero%2Cbelle-says%2Cbellesa-house-party&filter%5Bsource%5D=bellesa&limit=24&page=<PAGE>"
        if "bellesaplus.co" in base:
            pagination = "/api/rest/v1/videos?filter%5Bprovider%5D=or%3Abellesa-films%2Cbellesa-house%2Cbellesa-blind-date%2Czero-to-hero%2Cbelle-says%2Cbellesa-house-party&limit=24&page=<PAGE>&sources=plus"
        link = self.format_url(base, pagination.replace("<PAGE>", str(page)))
        return link

    async def start(self):
        for link in self.start_urls:
            api_url = self.get_next_page_url(link, self.page)
            if 'bellesaplus.co' in link:
                # Route through FlareSolverr to defeat CF's managed challenge.
                yield self._flare_request(api_url, page=self.page, base_link=link)
            else:
                # www.bellesa.co has no CF challenge — request the API directly.
                yield scrapy.Request(
                    url=api_url,
                    callback=self.parse,
                    meta={'page': self.page, 'base_link': link},
                    headers=self.headers,
                    cookies=self.cookies,
                )

    def _flare_request(self, target_url, page, base_link):
        """Wrap a URL in a POST to FlareSolverr and hand the response to parse_flare()."""
        payload = {
            'cmd': 'request.get',
            'url': target_url,
            'maxTimeout': 60000,
            # Pass our subscriber cookies through so FlareSolverr's browser sends
            # them when it hits the API after solving CF.
            'cookies': [
                {'name': c['name'], 'value': c['value'], 'domain': c.get('domain', 'bellesaplus.co')}
                for c in self.cookies
            ],
        }
        flare_url = self.settings.get('FLARE_ADDRESS')
        if not flare_url:
            self.logger.error("FLARE_ADDRESS not configured in settings")
            return None
        return scrapy.Request(
            url=flare_url,
            method='POST',
            body=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            callback=self.parse_flare,
            meta={'page': page, 'base_link': base_link, 'target_url': target_url},
            dont_filter=True,
        )

    def parse_flare(self, response):
        """Unwrap the FlareSolverr envelope and feed the inner body to parse()."""
        try:
            envelope = response.json()
        except ValueError:
            self.logger.error(f"FlareSolverr returned non-JSON: {response.text[:300]}")
            return
        if envelope.get('status') != 'ok':
            self.logger.error(f"FlareSolverr status={envelope.get('status')}: {envelope.get('message')}")
            return

        solution = envelope.get('solution', {})
        inner_status = solution.get('status')
        body = solution.get('response') or ''
        if inner_status != 200:
            self.logger.error(f"CF-cleared request still returned {inner_status}: {body[:300]}")
            return

        # Wrap the raw body back into a Scrapy Response so parse() sees it normally.
        from scrapy.http import TextResponse
        target_url = response.meta.get('target_url') or solution.get('url')
        synthetic = TextResponse(
            url=target_url,
            body=body.encode('utf-8'),
            encoding='utf-8',
            request=scrapy.Request(url=target_url, meta=response.meta),
        )
        yield from self.parse(synthetic)

    def parse(self, response, **kwargs):
        """Override so that bellesaplus.co next-page requests re-enter FlareSolverr."""
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if not count:
            return
        if 'page' not in response.meta or response.meta['page'] >= self.limit_pages:
            return

        meta = dict(response.meta)
        meta['page'] = meta['page'] + 1
        base = meta.get('base_link') or response.url
        next_url = self.get_next_page_url(base, meta['page'])
        print(f"NEXT PAGE: {meta['page']}")

        if 'bellesaplus.co' in base:
            yield self._flare_request(next_url, page=meta['page'], base_link=base)
        else:
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta=meta,
                headers=self.headers,
                cookies=self.cookies,
            )

    def get_scenes(self, response):
        if "</pre>" in response.text.lower():
            raw_json = response.css("pre::text").get()
        else:
            raw_json = response.text
        if "</pre>" in raw_json.lower():
            raw_json = re.search(r'<pre.*?>(.*?)<\/pre>', raw_json, re.DOTALL | re.IGNORECASE).group(1)

        jsondata = json.loads(raw_json)
        for scene in jsondata:
            item = self.init_scene()

            if scene['title']:
                item['title'] = self.cleanup_title(scene['title'].replace("&", "and"))
            else:
                item['title'] = None
            if scene['description']:
                item['description'] = self.cleanup_description(scene['description'])
            else:
                item['description'] = ''
            item['duration'] = scene['duration']
            datetime_obj = datetime.fromtimestamp(scene['posted_on'])
            item['date'] = datetime_obj.strftime('%Y-%m-%d')
            if self.check_item(item, self.days):
                item['id'] = scene['id']
                item['performers'] = []
                for performer in scene['performers']:
                    item['performers'].append(performer['name'])
                item['tags'] = scene['tags'].split(",")
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))
                item['tags'] = self.clean_tags(item['tags'], item['performers'])
                item['tags'].append("Unscripted")
                item['tags'].append("Ethical Porn")
                item['image'] = self.format_link(response, scene['image'])
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = None
                item['site'] = 'Bellessa House'
                item['parent'] = 'Bellessa House'
                item['network'] = 'Bellessa'
                if scene['content_provider']:
                    if 'name' in scene['content_provider'][0] and scene['content_provider'][0]['name']:
                        item['site'] = scene['content_provider'][0]['name']
                        item['parent'] = scene['content_provider'][0]['name']

                slug = slugify(re.sub('[^a-z0-9- ]', '', item['title'].lower().strip()))
                item['url'] = f"https://www.bellesa.co/videos/{item['id']}/{slug}"
                yield self.check_item(item, self.days)

    def clean_tags(self, tags, performers):
        tags2 = []
        for tag in tags:
            if "bellesa" not in tag.lower():
                if "original" not in tag.lower():
                    if tag not in performers:
                        if "." in tag:
                            tags = tag.split(".")
                            for tag in tags:
                                tags2.append(string.capwords(tag.strip()))
                        else:
                            tags2.append(tag)
        return tags2

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.status_code == 200:
                return req.content
        return None
