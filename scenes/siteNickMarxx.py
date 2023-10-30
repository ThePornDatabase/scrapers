import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNickMarxxSpider(BaseSceneScraper):
    name = 'NickMarxx'
    network = 'Nick Marxx'
    parent = 'Nick Marxx'
    site = 'Nick Marxx'

    start_url = 'https://nickmarxx.com'
    pagination = '/_next/data/<buildID>/videos.json?order_by=publish_date&sort_by=desc&type=&page=%s'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/videos.json?order_by=publish_date&sort_by=desc&type=&page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://nickmarxx.com/', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildID'] = buildId.group(1)
            meta['pagination'] = self.pagination
            link = self.get_next_page_url(self.start_url, self.page, meta['buildID'], self.pagination)
            yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['buildID'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, buildID, pagination):
        pagination = pagination.replace("<buildID>", buildID)
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['contents']['data']
        for scene in jsondata:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['description'] = self.cleanup_description(scene['description'])
            item['date'] = self.parse_date(re.search(r'(\d{4}/\d{2}/\d{2})', scene['publish_date']).group(1), date_formats=['%Y/%m/%d']).strftime('%Y-%m-%d')
            item['image'] = scene['thumb']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = scene['models']
            item['tags'] = scene['tags']
            if "seconds_duration" in scene:
                item['duration'] = scene['seconds_duration']
            else:
                item['duration'] = None
            item['trailer'] = scene['trailer_url']
            item['id'] = scene['id']
            item['url'] = f"https://nickmarxx.com/videos/{scene['slug']}"
            item['site'] = "Nick Marxx"
            item['parent'] = "Nick Marxx"
            item['network'] = "Nick Marxx"
            item['type'] = "Scene"
            yield self.check_item(item, self.days)
