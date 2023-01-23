import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
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
        meta={'dont_redirect': True,"handle_httpstatus_list": [302]}
        url = "https://www.femjoy.com"
        yield scrapy.Request(url, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "results_item")]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('./div/h1/a[1]/text()').get())
            item['date'] = self.parse_date(scene.xpath('./div//span[@class="posted_on"]/text()').get(), date_formats=['%b %d, %Y']).isoformat()
            item['duration'] = self.duration_to_seconds(scene.xpath('./div//span[@class="posted_on"]/following-sibling::span/text()').get())
            item['director'] = scene.xpath('.//h2/a[contains(@href, "/director/")]/text()').get()
            item['performers'] = scene.xpath('.//h2/a[contains(@href, "/models/")]/text()').getall()
            item['site'] = 'Femjoy'
            item['parent'] = 'Femjoy'
            item['network'] = 'Femjoy'
            item['type'] = 'Scene'
            item['url'] = self.format_link(response, scene.xpath('./div/div/a/@href').get())
            item['image'] = scene.xpath('./div/div/a/img[contains(@class, "item_cover")]/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            sceneid = re.search(r'\.com/post/(\d+)', item['url'])
            if sceneid:
                item['id'] = sceneid.group(1)
            item['tags'] = []
            item['trailer'] = ''
            meta['item'] = item
            yield scrapy.Request(item['url'], callback=self.get_description, headers=self.headers, cookies=self.cookies, meta=meta)

    def get_description(self, response):
        item = response.meta['item']
        description = response.xpath('//h2[@class="post_description"]/p')
        if description:
            item['description'] = description.get().strip()
        else:
            item['description'] = ''

        yield self.check_item(item, self.days)

    def get_next_page_url(self, base, page):
        if page > 1:
            pagination =  self.get_selector_map('pagination') % page
        else:
            pagination = '/videos'
        return self.format_url(base, pagination)
