import scrapy
import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAnalJesseSpider(BaseSceneScraper):
    name = 'AnalJesse'
    network = 'Anal Jesse'

    start_url = 'https://analjesse.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/tags/main.json?slug=main&page=%s&per_page=12'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://analjesse.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
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
                meta = response.meta
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
                item['site'] = "Anal Jesse"
                item['parent'] = "Anal Jesse"
                item['network'] = "Anal Jesse"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'] = []
                if "models_slugs" in scene:
                    for performer in scene['models_slugs']:
                        item['performers'].append(performer['name'])
                item['date'] = self.parse_date(scene['publish_date']).isoformat()
                item['id'] = scene['id']
                if scene['videos_duration']:
                    item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['image'] = scene['thumb'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['tags'] = []
                item['trailer'] = scene['poster_url'].replace(" ", "%20")
                item['url'] = f"https://analjesse.com/trailers/{scene['slug']}"

                yield self.check_item(item, self.days)
