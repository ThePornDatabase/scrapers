import re
import json
import scrapy
import string
from tpdb.helpers.http import Http
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTheArtemixxxSpider(BaseSceneScraper):
    name = 'TheArtemixxx'

    start_url = 'https://theartemixxx.com/'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/videos.json?series=&order_by=publish_date&sort_by=desc&page=%s',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://theartemixxx.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

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
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['pageProps']['contents']['data']
        for scene in jsondata:
            meta['id'] = scene['id']
            link = f"https://theartemixxx.com/_next/data/{meta['buildID']}/videos/{scene['slug']}.json"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['content']
        item = self.init_scene()
        item['site'] = "TheArtemixxx"
        item['parent'] = "TheArtemixxx"
        item['network'] = "TheArtemixxx"
        if "seconds_duration" in jsondata and jsondata['seconds_duration']:
            item['duration'] = str(jsondata['seconds_duration'])
        item['title'] = self.cleanup_title(string.capwords(jsondata['title']))
        if 'description' in jsondata and jsondata['description']:
            item['description'] = self.cleanup_text(jsondata['description'])
        item['performers_data'] = []
        for model in jsondata['models_thumbs']:
            model_page = f"https://theartemixxx.com/_next/data/{response.meta['buildID']}/models/{model['slug']}.json?slug={model['slug']}"
            req = Http.get(model_page)
            if req:
                model_page = json.loads(req.content)
                model_page = model_page['pageProps']['model']
            perf = {}
            perf['extra'] = {}
            perf['extra']['gender'] = model_page['gender']
            perf['name'] = string.capwords(model['name'])
            perf['image'] = model['thumb'].replace(" ", "%20")
            perf['image_blob'] = self.get_image_blob_from_link(model['thumb'])
            perf['site'] = "TheArtemixxx"
            perf['network'] = "TheArtemixxx"
            item['performers_data'].append(perf)
            item['performers'].append(string.capwords(model['name']))

        item['date'] = self.parse_date(jsondata['publish_date'], date_formats=['%Y/%m/%d']).strftime('%Y-%m-%d')

        item['id'] = jsondata['id']
        item['image'] = jsondata['thumb'].replace(" ", "%20")
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['tags'] = jsondata['tags']
        item['url'] = f"https://theartemixxx.com/videos/{jsondata['slug']}"

        yield self.check_item(item, self.days)
