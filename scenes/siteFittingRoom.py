import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.utils.project import get_project_settings


class FittingRoomSpider(BaseSceneScraper):
    name = 'FittingRoom'
    network = 'Fitting Room'
    parent = 'Fitting Room'
    site = 'Fitting Room'

    start_url = 'https://www.fitting-room.com/'

    paginations = [
        '/extras/%s/',
        '/videos/%s/',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': "",
        'performers': '//div[@class="info-model"]/p[@class="name"]/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//meta[@property="article:tag"]/@content',
        'external_id': r'videos\/(\d+)\/?',
        'trailer': '//script[contains(text(),"video_url")]/text()',
        're_trailer': r'video_url:\ .*?(https:\/\/www\.fitting.*?\.mp4)',
        'pagination': '/extras/%s/'
    }

    def start_requests(self):
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

        for pagination in self.paginations:
            link = self.start_url
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['pagination']),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response):
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"thumb videos")]/a')
        for scene in scenes:
            date = scene.xpath('./div[@class="main-info"]/div/p/text()').get()
            date = self.parse_date(date.strip()).isoformat()
            sceneurl = scene.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta={'date': date})
