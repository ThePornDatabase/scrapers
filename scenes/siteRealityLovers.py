import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteRealityLoversSpider(BaseSceneScraper):
    name = 'RealityLovers'
    network = 'Reality Lovers'
    parent = 'Reality Lovers'
    site = 'Reality Lovers'

    start_urls = [
        'https://engine.realitylovers.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/content/videos?max=12&page=%s&pornstar=&category=&perspective=&sort=NEWEST',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [307,404],
        'HANDLE_HTTPSTATUS_LIST': [307,404],
        "HTTPCACHE_ENABLED": False,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['reg_pagination'] = "https://realitylovers.com/videos/page%s"
        meta['json_pagination'] = f"https://engine.realitylovers.com/content/videos?max=12&page=%s&pornstar=&category=&perspective=&sort=NEWEST"

        link = "https://realitylovers.com/"
        yield scrapy.Request(link, callback=self.start_requests_primed, meta=meta)

    def start_requests_primed(self, response):
        meta = response.meta
        for link in self.start_urls:
            meta['link'] = link
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['reg_pagination']), callback=self.start_requests_2, meta=meta)

    def start_requests_2(self, response):
        meta = response.meta
        yield scrapy.Request(url=self.get_next_page_url(meta['link'], self.page, meta['json_pagination']), callback=self.parse, meta=meta)


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
                url = self.get_next_page_url(response.url, meta['page'], meta['reg_pagination'])
                print('NEXT PAGE: ' + str(meta['page']) + f"  Url: {url}")
                yield scrapy.Request(url, callback=self.mid_index, meta=meta)

    def mid_index(self, response):
        meta = response.meta
        yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['json_pagination']), callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = json.loads(response.text)
        for scene in scenes['contents']:
            sceneid = scene['id']
            if sceneid:
                meta['link'] = f"https://engine.realitylovers.com/content/videoDetail?contentId={sceneid}"
                link = f"https://realitylovers.com/{scene['videoUri']}"
                yield scrapy.Request(link, callback=self.mid_scene, meta=meta)

    def mid_scene(self, response):
        meta = response.meta
        link = meta['link']
        yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        scene = json.loads(response.text)
        item = SceneItem()

        item['title'] = self.cleanup_title(scene['title'])
        item['description'] = re.sub(r'<[^<]+?>', '', self.cleanup_description(scene['description']))
        item['date'] = scene['releaseDate']
        item['performers'] = []
        if "starring" in scene:
            for performer in scene['starring']:
                item['performers'].append(self.cleanup_title(performer['name']))

        item['tags'] = []
        if "categories" in scene:
            for tag in scene['categories']:
                item['tags'].append(self.cleanup_title(tag['name']))

        item['url'] = f"https://realitylovers.com/{scene['canonicalUri']}"
        item['id'] = scene['contentId']
        image = ''
        if 'mainImages' in scene:
            if len(scene['mainImages']):
                image = scene['mainImages'][0]['imgSrcSet']
                image = re.search(r'(.*?) ', image).group(1)

        if image:
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(image)
        else:
            item['image'] = ''
            item['image_blob'] = ''

        item['type'] = 'Scene'
        if 'trailerUrl' in scene:
            item['trailer'] = scene['trailerUrl']
        item['site'] = "Reality Lovers"
        item['parent'] = "Reality Lovers"
        item['network'] = "Reality Lovers"

        yield self.check_item(item, self.days)
