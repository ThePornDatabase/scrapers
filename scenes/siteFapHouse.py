import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFapHouseSpider(BaseSceneScraper):
    name = 'FapHouse'

    start_url = 'https://faphouse.com'

    paginations = [
        ['https://faphouse.com/studios/private-society?page=%s', 'Private Society'],
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[contains(@class, "description")]//p/text()',
        'date': '//span[@class="video-publish-date"]/text()',
        're_date': r'(\d{1,2}\.\d{1,2}\.\d{4})',
        'date_formats': ['%d.%m.%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@data-el="RelatedTags"]//a[contains(@href, "/pornstars/")]/span[2]/text()',
        'tags': '//div[@data-el="RelatedTags"]//a[contains(@class, "__category") and contains(@href, "/videos")]/text()',
        'duration': '//span[contains(@class, "video-duration")]/text()',
        'external_id': r'.*/(.*?)$',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination[0]
            meta['site'] = pagination[1]
            meta['parent'] = pagination[1]
            meta['network'] = pagination[1]
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="thumb__main"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        item = SceneItem()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = response.meta['site']
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None

        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = ''
            item['image_blob'] = ''

        if item['image']:
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = response.meta['network']
        item['parent'] = response.meta['parent']
        item['type'] = 'Scene'

        allow_site = True
        if 'ignore_sites' in response.meta:
            ignore_sites = response.meta['ignore_sites']
            ignore_sites = ignore_sites.split(",")
            for ignore_site in ignore_sites:
                ignore_site = re.sub('[^0-9a-zA-Z]', '', ignore_site.lower())
                site = re.sub('[^0-9a-zA-Z]', '', item['site'].lower())
                if site == ignore_site:
                    allow_site = False

        if "Private Society" in item['site']:
            if item['date'] < '2022-09-22':
                allow_site = False

        if allow_site:
            yield self.check_item(item, self.days)
        else:
            print(f"*** Not processing item due to disallowed site or date: {item['site']}")
