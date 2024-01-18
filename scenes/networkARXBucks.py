import json
import re
from scrapy.http import Request
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkARXBucksSpider(BaseSceneScraper):
    name = 'ARXBucks'

    start_url = "https://arx-graphql-8b05680a5a0f.herokuapp.com/v1/graphql"

    headers = {
        "Content-Type": "application/json"
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        payload = self.get_next_page(self.page)
        yield Request(self.start_url, headers=self.headers, body=payload, method="POST", callback=self.parse, meta=meta, dont_filter=True)

    def parse(self, response, **kwargs):
        meta = response.meta
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
                payload = self.get_next_page(meta['page'])
                yield Request(self.start_url, headers=self.headers, body=payload, method="POST", meta=meta, callback=self.parse, dont_filter=True)

    def get_next_page(self, page):
        true = True
        data = {
            "operationName": "SiteScenes",
            "variables": {
                "where": {"isAvailable": {"_eq": true}},
                "orderBy": {"availableAt": "DESC"},
                "limit": 18,
                "offset": (int(page) - 1) * 18},
            "query": "query SiteScenes($where: SiteScenesBoolExp = {}, $orderBy: [SiteScenesOrderBy!] = [], $limit: Int = 20, $offset: Int = 0) {siteScenes(where: $where, limit: $limit, offset: $offset, orderBy: $orderBy) {id availableAt scene {id title summary durationText quality createdAt urls {id urlPath thumbnailUrl} sceneActors{actor{id stageName gender dob urls{id url thumbnailUrl}}} sceneGenres{genre{id name slug}} sceneSites{site{id name}}}}}"
        }
        payload = json.dumps(data)
        return payload

    selector_map = {
        'external_id': r'',
        'pagination': ''
    }

    def get_scenes(self, response):
        jsondata = response.json()['data']['siteScenes']
        for jsonrow in jsondata:
            item = SceneItem()
            if jsonrow['availableAt']:
                item['date'] = jsonrow['availableAt']
            else:
                item['date'] = jsonrow['scene']['createdAt']
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', item['date']).group(1)
            jsonrow = jsonrow['scene']
            item['id'] = jsonrow['id']
            item['title'] = jsonrow['title']
            if len(jsonrow['sceneSites']):
                item['site'] = jsonrow['sceneSites'][0]['site']['name']
                prefix = f"https://{item['site'].lower().replace(' ', '')}.com"
            else:
                item['site'] = "ARXBucks"
                prefix = "https://arxbucks.com"
            item['parent'] = item['site']
            item['network'] = "ARX Bucks"

            item['url'] = prefix + jsonrow['urls']['urlPath']
            item['image'] = jsonrow['urls']['thumbnailUrl']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = ''
            item['description'] = jsonrow['summary']

            item['tags'] = []
            for tag in jsonrow['sceneGenres']:
                item['tags'].append(tag['genre']['name'])

            item['performers'] = []
            for performer in jsonrow['sceneActors']:
                item['performers'].append(performer['actor']['stageName'])

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
