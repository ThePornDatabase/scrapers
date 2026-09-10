import re
import json
import pycountry
import requests
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMILFLiciousSpider(BaseSceneScraper):
    name = 'MILFLicious'

    start_url = 'https://milflicious.com/'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/videos.json?page=%s&order_by=publish_date&sort_by=desc'
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://milflicious.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

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
        meta = self.copy_meta(response)
        jsondata = json.loads(response.text)
        if jsondata:
            jsondata = jsondata['pageProps']['contents']
            for scene in jsondata['data']:
                item = SceneItem()
                item['site'] = "MILFLicious"
                item['parent'] = "Radical Entertainment"
                item['network'] = "Radical Entertainment"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'] = []
                item['performers_data'] = []
                if "models_slugs" in scene:
                    for performer in scene['models_slugs']:
                        perf_url = f"https://milflicious.com/_next/data/{meta['buildID']}/models/{performer['slug']}.json?slug={performer['slug']}"
                        perf, perf_data = self.get_performer(perf_url)
                        if perf:
                            item['performers'].append(perf)
                        if perf_data:
                            item['performers_data'].append(perf_data)
                item['date'] = self.parse_date(scene['publish_date']).isoformat()
                item['id'] = scene['id']
                if scene['videos_duration']:
                    item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['image'] = scene['thumb'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['tags'] = scene['tags']
                item['trailer'] = scene['trailer_url'].replace(" ", "%20")
                item['url'] = f"https://milflicious.com/{scene['slug']}"

                yield self.check_item(item, self.days)

    def get_performer(self, url):
        response = requests.get(url, headers=self.headers, cookies=self.cookies)
        data = json.loads(response.text)
        if data:
            data = data['pageProps']['model']
            perf_data = {}
            perf_data['extra'] = {}

            perf = data['name']
            perf_data['name'] = perf
            perf_data['image'] = data['thumb'].replace(" ", "%20")
            perf_data['image_blob'] = self.get_image_blob_from_link(perf_data['image'])
            perf_data['url'] = f"https://milflicious.com/models/{data['slug']}"
            perf_data['id'] = data['slug']
            perf_data['site'] = "MILFLicious"
            perf_data['network'] = "Radical Entertainment"
            if "gender" in data and data['gender']:
                perf_data['extra']['gender'] = string.capwords(data['gender'])
            else:
                perf_data['extra']['gender'] = "Female"
            if "Bio" in data and data['Bio']:
                perf_data['bio'] = self.cleanup_text(data['Bio'])
            elif "details" in data and data['details']:
                perf_data['bio'] = self.cleanup_text(re.sub(r'<[^>]+>', '', data['details']))

            if "Country" in data and data['Country']:
                perf_data['extra']['birthplace'] = string.capwords(data['Country'])
                country_code = pycountry.countries.get(name=data['Country'])
                if country_code:
                    perf_data['extra']['birthplace_code'] = country_code.alpha_2
            return perf, perf_data
        return None, None
