import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteYesGirlzBTSSpider(BaseSceneScraper):
    name = 'YesGirlzBTS'

    start_url = 'https://yesgirlz.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/bonus.json?page=%s&order_by=publish_date&sort_by=desc',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://yesgirlz.com/', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

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
        jsondata = response.json()
        jsondata = jsondata['pageProps']['contents']['data']
        for scene in jsondata:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['id'] = scene['id']
            item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description']))
            item['image'] = self.format_link(response, scene['thumb']).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if scene['trailer_url']:
                item['trailer'] = self.format_link(response, scene['trailer_url']).replace(" ", "%20")
            else:
                item['trailer'] = ""
            scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).isoformat()
            item['date'] = ""
            if scene_date:
                item['date'] = scene_date
            item['url'] = f"https://yesgirlz.com/scenes/{scene['slug']}"
            item['tags'] = []
            if "tags" in scene:
                item['tags'] = scene['tags']
            item['tags'].append("BTS")
            item['duration'] = scene['seconds_duration']
            item['site'] = 'YesGirlz'
            item['parent'] = 'YesGirlz'
            item['network'] = 'YesGirlz'
            item['performers'] = []
            for model in scene['models_slugs']:
                item['performers'].append(model['name'])

            yield self.check_item(item, self.days)
