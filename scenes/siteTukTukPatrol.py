import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTukTukPatrolSpider(BaseSceneScraper):
    name = 'TukTukPatrol'

    start_urls = [
        'https://tuktukpatrol.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/page-data/all-updates/%s/page-data.json'
    }

    def get_next_page_url(self, base, page):
        if page == 1:
            return "https://tuktukpatrol.com/page-data/all-updates/page-data.json"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsondata = jsondata['result']
        for scene in jsondata['data']['post']['nodes']:
            scenelink = f"https://tuktukpatrol.com/page-data/content/{scene['slug']}/page-data.json"
            yield scrapy.Request(scenelink, callback=self.get_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scene(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['result']['data']['post']
        item = SceneItem()

        item['title'] = jsondata['title'].replace("\r", "").replace("\n", " ").replace("  ", " ")
        item['description'] = re.sub(r'<.*?>', '', jsondata['content']).replace("\r", "").replace("\n", " ").replace("  ", " ")
        item['date'] = self.parse_date(jsondata['date'], date_formats=['%B %d, %Y']).isoformat()
        item['image'] = jsondata['contentData']['posterImage']['mediaItemUrl']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['performers'] = []
        for model in jsondata['model']['nodes']:
            item['performers'].append(model['modelInfo']['name'])
        item['tags'] = []
        for tag in jsondata['categories']['nodes']:
            item['tags'].append(tag['acfCategoryData']['categoryNiceName'])
        item['url'] = self.format_link(response, jsondata['link'])
        item['id'] = jsondata['slug']
        item['duration'] = self.duration_to_seconds(jsondata['contentData']['duration'])
        item['trailer'] = ''
        item['network'] = "Vegas Dreamworks"
        item['site'] = "TukTuk Patrol"
        item['parent'] = "TukTuk Patrol"

        yield self.check_item(item, self.days)
