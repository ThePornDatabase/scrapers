import re
from datetime import datetime
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class VIP4KSpider(BaseSceneScraper):
    name = 'VIP4K'
    network = 'VIP 4K'
    parent = 'VIP 4K'

    start_urls = [
        'https://black4k.com',
        'https://daddy4k.com',
        'https://fist4k.com',
        'https://mature4k.com',
        'https://old4k.com',
        'https://rim4k.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"item__title")]/text() | //h1[contains(@class,"info__title")]/text() | //div[@class="title_player"]/text() | //div[@class="title"]/text()',
        'description': '//div[contains(@class,"player-item__text")]/text() | //span[@class="player-info__text-area"]/text() | //div[@class="desc_frame"]/p/text() | //div[@class="wrap_post"]/p/text() | //div[@class="wrap_player_desc"]/p/text()',
        'date': '',
        'image': '//div[@class="player-item__block"]//img/@data-src | //div[@class="player_watch"]/img/@src',
        'performers': '//div[@class="player-item__about"]//div[@class="item-info__text"]/text()',
        'tags': "",
        'external_id': r'videos\/(\d+)',
        'trailer': '//video/source/@src',
        'pagination': '/en/%s'
    }

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count and "nothinghere" not in response.url:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        scenes = []
        if "black4k" in response.url:
            scenes = response.xpath('//div[@class="box_row"][1]//div[@class="thumb_wrap"]/a/@href').getall()
        if "daddy4k" in response.url:
            scenes = response.xpath('//div[@class="thumb"]/div[@class="th"]/a[contains(@href,"/en/videos/")]/@href').getall()
        if "old4k" in response.url:
            scenes = response.xpath('//div[@class="thumbs_items"]/div[@class="th_item"]/a[contains(@href,"/en/videos/")]/@href').getall()
        if "rim4k" in response.url:
            scenes = response.xpath('//a[contains(@class, "item__main")]/@href').getall()
        if not scenes:
            scenes = response.xpath('//a[@class="item__title"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        return datetime.now().isoformat()

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            if image[:2] == "//":
                image = "https:" + image
            return self.format_link(response, image)
        return ''

    def get_performers(self, response):
        if "fist4k" in response.url:
            performers = response.xpath('//div[@class="player-item__about"]//div[@class="item-info__text"]/text()').getall()
            if performers:
                performer = performers[-2].strip()
        if "black4k" in response.url or "old4k" in response.url:
            performers = response.xpath('//div[@class="cat_player"]/a[contains(@href,"/models/")]/text()').get()
            if performers:
                performer = performers.strip()
        if "mature4k" in response.url:
            performers = response.xpath('//a[@class="item-info__item item-info__item--hid2"]/div[@class="item-info__text"]/text()').get()
            if performers:
                performer = performers.strip()
        if "rim4k" in response.url:
            performers = response.xpath('//div[@class="player-item__about"]/ul/li[3]/div[@class="item-info__text"]/text()').getall()
            if performers:
                performers = "".join(performers)
                performers = performers.replace('\n', '').replace('\r', '').replace('  ', ' ')
                if ',' in performers:
                    performers = performers.split(',')
                    performers = list(map(lambda x: x.strip().title(), performers))
                    return performers
                performer = performers.strip()
        if "daddy4k" in response.url:
            return []
        if performers:
            return [performer]
        return []

    def get_tags(self, response):
        tags = []
        if "black4k" in response.url:
            tags = response.xpath('//div[@class="tag_line"]/a/span/text()').getall()
            tags = list(map(lambda x: x.strip().title(), tags))
        if "daddy4k" in response.url or "old4k" in response.url:
            tags = response.xpath('//a[@class="item_tag"]/span/text()').getall()
            tags = list(map(lambda x: x.strip().title(), tags))
        if "rim4k" in response.url:
            tags.append('Rimming')
        if tags:
            return tags
        return []

    def get_trailer(self, response):
        return ''

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        search = search.zfill(4).strip()

        return search

    def get_next_page_url(self, base, page):
        pagination = False
        if "black4k" in base or "daddy4k" in base or "old4k" in base:
            if page == 1:
                pagination = "/en/videos/publish"
            else:
                pagination = "/nothinghere/"
        if "mature4k" in base or "fist4k" in base:
            if page == 1:
                pagination = "/en/"
            else:
                pagination = "/nothinghere/"

        if not pagination:
            pagination = self.get_selector_map('pagination') % page

        return self.format_url(base, pagination)
