# The reson for this is that 3x used to have sites, but they've consolidated and those sites are now "Series"
# Unfortunately they make no distinction between the sites on the index, and instead you have the pull from specific
# indexes.  So this will pull the sub indexes, and write out the results to a dupefile to check against for the
# non-proper pull
import os.path
import re
from pathlib import Path
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class Only3XProperSpider(BaseSceneScraper):
    name = 'Only3XProper'
    network = 'Only 3X'
    parent = 'Only 3X'

    start_url = 'https://only3x.com'

    paginations = [
        ['/watch-newest-only-3x-clips-and-scenes.html?page=%s&series=51447&hybridview=member', 'Just Anal'],
        ['/watch-newest-only-3x-clips-and-scenes.html?page=%s&series=51467&hybridview=member', 'Only 3x VR'],
        ['/watch-newest-only-3x-clips-and-scenes.html?page=%s&series=51450&hybridview=member', 'Only Gold Digger'],
        ['/watch-newest-only-3x-clips-and-scenes.html?page=%s&series=51448&hybridview=member', 'Only 3x Girls'],
        ['/watch-newest-only-3x-clips-and-scenes.html?page=%s&series=51585&hybridview=member', 'Only 3x Lost'],
        ['/watch-newest-only-3x-clips-and-scenes.html?page=%s&series=51449&hybridview=member', 'Pure BJ'],
        ['/watch-newest-only-3x-clips-and-scenes.html?page=%s&series=60751&hybridview=member', 'Whore House']
    ]

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//div[@class="synopsis"]//text()',
        'date': '//span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'duration': '//span[contains(text(), "Length")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-performer"]/a//text()',
        'tags': '//span[contains(text(), "Tags")]/following-sibling::a[@data-label="Tag"]/text()',
        'external_id': r'/(\d+)/',
        'trailer': '',
        'pagination': '/watch-newest-only-3x-clips-and-scenes.html?page=%s&hybridview=member'
    }

    def start_requests(self):
        meta = {}
        for pagination in self.paginations:
            meta['site'] = pagination[1]
            meta['pagination'] = pagination[0]
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
        scenes = response.xpath(
            '//article/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//span[contains(text(), "Studio:")]/following-sibling::span/text()')
        if site:
            return site.get().strip()
        super.get_site(response)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            scenelength = 0
            duration = duration.get()
            if "min" in duration:
                duration = re.search(r'(\d+) min', duration)
                if duration:
                    minutes = duration.group(1)
                    scenelength = scenelength + (int(minutes) * 60)
            return str(scenelength)
        return ""

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = meta['site']
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        if 'image' not in item or not item['image']:
            item['image'] = None
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image_blob'] = None
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = self.get_parent(response)
        item['type'] = 'Scene'

        if self.check_item(item, self.days):
            if not os.path.exists('dupelist-only3x.txt'):
                Path('dupelist-only3x.txt').touch()
            with open('dupelist-only3x.txt', 'a', encoding="utf-8") as file1:
                file1.write(item['id'] + "|" + response.url + "\n")
            yield item
