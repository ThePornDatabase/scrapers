import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
false = False
true = True


class SiteFemjoySpider(BaseSceneScraper):
    name = 'Femjoy'
    network = 'Femjoy'
    parent = 'Femjoy'
    site = 'Femjoy'

    start_urls = [
        'https://www.femjoy.com',
    ]

    headers = {'referer': 'https://www.femjoy.com/videos'}

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta = {'dont_redirect': True, "handle_httpstatus_list": [302]}
        url = "https://www.femjoy.com"
        yield scrapy.Request(url, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "results_item")]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.cleanup_title(scene.xpath('./div/h1/a[1]/text()').get())
            item['date'] = self.parse_date(scene.xpath('./div//span[@class="posted_on"]/text()').get(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
            duration = scene.xpath('.//h3/span/i/following-sibling::text()').get()
            if duration:
                item['duration'] = self.duration_to_seconds(duration.strip())
            item['director'] = scene.xpath('.//h2/span[contains(text(), "by")]/following-sibling::a/text()').get()
            item['performers'] = scene.xpath('.//h2/span[contains(text(), "by")]/preceding-sibling::a/text()').getall()
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))
            item['site'] = 'Femjoy'
            item['parent'] = 'Femjoy'
            item['network'] = 'Femjoy'
            item['type'] = 'Scene'
            item['image'] = scene.xpath('./div/div/a/img[contains(@class, "item_cover")]/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            sceneid = scene.xpath('./div[1]/@data-post-id')
            if sceneid:
                item['id'] = sceneid.get().strip()
                item['url'] = f"https://www.femjoy.com/post/{item['id']}"
            item['tags'] = []
            item['trailer'] = ''
            # ~ if item['id']:
            yield self.check_item(item, self.days)

    def get_next_page_url(self, base, page):
        if page > 1:
            pagination = self.get_selector_map('pagination') % page
        else:
            pagination = '/videos'
        return self.format_url(base, pagination)
