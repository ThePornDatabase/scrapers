import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteXXXTryoutSpider(BaseSceneScraper):
    name = 'XXXTryout'
    network = 'XXX Tryout'
    parent = 'XXX Tryout'
    site = 'XXX Tryout'

    start_url = 'https://xxxtryout.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/videos.json?page=%s&order_by=publish_date&sort_by=desc'
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://xxxtryout.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = self.copy_meta(response)
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildID'] = buildId.group(1)
            link = self.get_next_page_url(self.start_url, self.page, meta['buildID'])
            yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['buildID']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, buildID):
        pagination = self.get_selector_map('pagination')
        pagination = pagination.replace("<buildID>", buildID)
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        if jsondata:
            jsondata = jsondata['pageProps']['contents']
            for scene in jsondata['data']:
                item = SceneItem()
                item['site'] = "XXX Tryout"
                item['parent'] = "XXX Tryout"
                item['network'] = "XXX Tryout"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'], item['performers_data'] = self.get_performers_data(scene['models_thumbs'])
                item['date'] = self.parse_date(scene['publish_date']).isoformat()
                item['id'] = scene['id']
                if scene['videos_duration']:
                    item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['image'] = scene['thumb'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['tags'] = scene['tags']
                item['trailer'] = scene['trailer_url'].replace(" ", "%20")
                item['url'] = f"https://xxxtryout.com/videos/{scene['slug']}"

                yield self.check_item(item, self.days)

    def get_performers_data(self, models):
        performers = []
        performers_data = []
        for model in models:
            performers.append(model['name'])
            performers_data.append({
                "name": model['name'],
                "image": model['thumb'],
                "gender": model['gender'],
                "image_blob": self.get_image_blob_from_link(model['thumb']),
                "site": "XXX Tryout",
                "network": "XXX Tryout"
            })
        return performers, performers_data
