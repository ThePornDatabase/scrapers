import re
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNastyDaddySpider(BaseSceneScraper):
    name = 'NastyDaddy'

    start_url = 'https://nastydaddy.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/videos.json?order_by=publish_date&sort_by=desc&site=&page=%s'
                      
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://nastydaddy.com/', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

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
        jsondata = response.json()
        jsondata = jsondata['pageProps']['contents']['data']
        for scene in jsondata:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['id'] = scene['id']
            item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description']))
            item['trailer'] = self.format_link(response, scene['trailer_url']).replace(" ", "%20")
            scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).isoformat()
            item['date'] = ""
            if scene_date:
                item['date'] = scene_date
            item['url'] = f"https://nastydaddy.com/videos/{scene['slug']}"
            item['tags'] = []  # Tags only return breast size
            # ~ if "tags" in scene:
            # ~ item['tags'] = scene['tags']
            item['duration'] = scene['seconds_duration']
            item['site'] = 'NastyDaddy'
            item['parent'] = 'NastyDaddy'
            item['network'] = 'NastyDaddy'
            item['performers'] = []
            for model in scene['models_slugs']:
                item['performers'].append(model['name'])
            item['performers_data'] = self.get_performers_data(item['performers'])

            if item['date'] and item['date'] > "2025-11-15":
                item['image'] = self.format_link(response, scene['trailer_screencap']).replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                yield self.check_item(item, self.days)

    def get_performers_data(self, performers):
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "NastyDaddy"
            performer_extra['site'] = "NastyDaddy"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data