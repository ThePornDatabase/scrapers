import re
from urllib.parse import urlsplit, urlunsplit, quote
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDickHDDailySpider(BaseSceneScraper):
    name = 'DickHDDaily'
    network = 'DickHDDaily'
    parent = 'DickHDDaily'
    site = 'DickHDDaily'

    start_url = 'https://dickhddaily.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/videos.json?page=%s&order_by=publish_date&sort_by=desc',
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://dickhddaily.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

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

    @staticmethod
    def clean_url(url):
        """Percent-encode unsafe characters (e.g. spaces) in the URL path so the
        upstream feed's typo-ridden filenames still resolve."""
        if not url:
            return url
        parts = urlsplit(url)
        return urlunsplit(parts._replace(path=quote(parts.path, safe='/')))

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['contents']['data']
        for scene in jsondata:
            item = self.init_scene()
            item['title'] = self.cleanup_title(scene['title'])
            item['description'] = self.cleanup_description(scene['description'])
            item['date'] = self.parse_date(re.search(r'(\d{4}/\d{2}/\d{2})', scene['publish_date']).group(1), date_formats=['%Y/%m/%d']).strftime('%Y-%m-%d')
            item['image'] = self.clean_url(scene['trailer_screencap'])
            if ".mp4" not in item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['performers'], item['performers_data'] = self.get_performers_data(scene['models_thumbs'])
            item['tags'] = scene['tags']
            if "seconds_duration" in scene:
                item['duration'] = scene['seconds_duration']
            else:
                item['duration'] = None
            item['id'] = scene['id']
            item['url'] = f"https://dickhddaily.com/videos/{scene['slug']}"
            item['site'] = "DickHDDaily"
            item['parent'] = "DickHDDaily"
            item['network'] = "DickHDDaily"
            item['type'] = "Scene"
            yield self.check_item(item, self.days)

    def get_performers_data(self, models):
        performers = []
        performers_data = []
        for model in models:
            thumb = self.clean_url(model['thumb'])
            performers.append(model['name'])
            performers_data.append({
                "name": model['name'],
                "image": thumb,
                "image_blob": self.get_image_blob_from_link(thumb),
                "site": "DickHDDaily",
                "network": "DickHDDaily"
            })
        return performers, performers_data