import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteCastingCouchHDAPISpider(BaseSceneScraper):
    name = 'CastingCouchHDAPI'
    network = 'CastingCouch-HD'
    parent = 'CastingCouch-HD'
    site = 'CastingCouch-HD'

    start_url = 'https://castingcouch-hd.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/index.json?page=%s&order_by=publish_date&sort_by=desc'
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://castingcouch-hd.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

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
            jsondata = jsondata['pageProps']
            for scene in jsondata['videos']:
                item = self.init_scene()
                item['site'] = "CastingCouch-HD"
                item['parent'] = "CastingCouch-HD"
                item['network'] = "NetVideoGirls"
                item['date'] = self.parse_date(scene['release_date']).strftime('%Y-%m-%d')
                if self.check_item(item, self.days):
                    item['title'] = self.cleanup_title(scene['short_title'])
                    if "latest cchd" in item['title'].lower():
                        item['title'] = scene['custom_title']
                    if "description" in scene and scene['description']:
                        item['description'] = self.cleanup_text(scene['description'])
                    if "models" in scene and scene['models']:
                        item['performers'], item['performers_data'] = self.get_performers_data(scene['models'])
                    item['id'] = scene['id']
                    if "video_duration" in scene and scene['video_duration']:
                        item['duration'] = scene['video_duration']
                    item['image'] = f"https://dist.castingcouch-hd.com/web-images/{scene['id']}-1-med.jpg"
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                    if "tags" in scene and scene['tags']:
                        item['tags'] = scene['tags']
                    item['url'] = f"https://castingcouch-hd.com/videos/{scene['content_f']}"

                    yield self.check_item(item, self.days)

    def get_performers_data(self, models):
        performers = []
        performers_data = []
        for model in models:
            model_name = model['model_name']
            if " " not in model_name:
                model_name = f"{model_name} {model['id']}"

            performers.append(model_name)
            performers_data.append({
                "name": model_name,
                "site": "CastingCouch-HD",
                "network": "NetVideoGirls",
                "extra": {"gender": "Female"}
            })
        return performers, performers_data
