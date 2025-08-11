import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkYezzclipsSpider(BaseSceneScraper):
    name = 'Yezzclips'

    start_urls = [
        ['One Two Pee', False, '1054'],
    ]

    cookies = [{"name": "confirmedage", "value": "1"}]

    selector_map = {
        'title': './/h4/text()',
        'description': './/h4//following-sibling::p/text()',
        'tags': './/text()[contains(., "Category:")]/following-sibling::a/text()',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, page, meta):
        link = f"https://www.yezzclips.com/store_view.php?id={str(meta['siteid'])}&page={str(page)}"
        return link

    def start_requests(self):
        url = "https://www.yezzclips.com"
        yield scrapy.Request(url, callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        self.headers['referer'] = 'https://www.yezzclips.com'

        for link in self.start_urls:
            meta['page'] = self.page
            meta['siteid'] = link[2]
            meta['site'] = link[0]
            meta['parse_performer'] = link[1]
            url=self.get_next_page_url(self.page, meta)
            yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response):
        # ~ print(response.text)
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta), callback=self.parse, meta=meta, headers=self.headers)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="row storeview_clip"]')
        for scene in scenes:
            item = self.init_scene()
            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            image = scene.xpath('.//div[contains(@class, "vidpreview")]/@data-staticimg')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            sceneid = scene.xpath('.//a[@role="button"]/@href')
            if sceneid:
                item['id'] = re.search(r'item_id=(\d+)', sceneid.get()).group(1)
                item['url'] = sceneid.get()
            item['site'] = "Yezzclips: " + meta['site']
            item['parent'] = "Yezzclips"
            item['network'] = "Yezzclips"
            item['performers'] = self.get_performers(response)
            item['tags'] = self.get_tags(scene)
            item['duration'] = self.get_duration(scene)
            yield self.check_item(item, self.days)

    def get_performers(self, response):
        return []

    def get_duration(self, response):
        duration = response.xpath('.//text()[contains(., "Length:") and contains(., "min")]')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]+', '', duration)
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None
