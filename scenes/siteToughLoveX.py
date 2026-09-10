import re
import string
from urllib.parse import urlsplit, urlunsplit, quote
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteToughLoveXSpider(BaseSceneScraper):
    name = 'ToughLoveX'
    network = 'Radical Entertainment'
    parent = 'ToughLoveX'
    site = 'ToughLoveX'

    start_url = 'https://tour.toughlovex.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/videos.json?page=%s&order_by=publish_date&sort_by=desc',
        'type': 'Scene',
    }

    # The scene JSON gives each model as {name, slug, thumb} with no gender, so the
    # model list is pulled once up front to build a slug -> gender map.
    models_url = '/_next/data/%s/models.json?page=1&per_page=1000&gender='

    async def start(self):
        self.genders = {}
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request(self.start_url, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = self.copy_meta(response)
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildID'] = buildId.group(1)
            link = self.format_url(self.start_url, self.models_url % meta['buildID'])
            yield scrapy.Request(link, callback=self.parse_models, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_models(self, response):
        meta = self.copy_meta(response)
        for model in response.json()['pageProps']['models']['data']:
            gender = self.clean_gender(model['gender'])
            if gender:
                self.genders[model['slug']] = gender
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
        """Percent-encode unsafe characters (e.g. spaces) in the URL path."""
        if not url:
            return url
        parts = urlsplit(url)
        return urlunsplit(parts._replace(path=quote(parts.path, safe='/')))

    @staticmethod
    def clean_gender(gender):
        """The feed mixes case ('female'/'Female') and uses 'shemale' for trans models."""
        if not gender:
            return None
        gender = string.capwords(gender.strip())
        if gender == 'Shemale':
            return 'Transgender Female'
        return gender

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
            if "seconds_duration" in scene and scene['seconds_duration']:
                item['duration'] = scene['seconds_duration']
            else:
                item['duration'] = None
            item['id'] = scene['id']
            item['url'] = f"{self.start_url}/videos/{scene['slug']}"
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['type'] = self.get_selector_map('type')
            yield self.check_item(item, self.days)

    def get_performers_data(self, models):
        performers = []
        performers_data = []
        for model in models:
            if not model.get('name'):
                continue
            name = string.capwords(model['name'])
            thumb = self.clean_url(model['thumb'])
            performers.append(name)
            performer = {
                "name": name,
                "image": thumb,
                "image_blob": self.get_image_blob_from_link(thumb),
                "site": self.site,
                "network": self.network,
            }
            gender = self.genders.get(model['slug'])
            if gender:
                performer['extra'] = {'gender': gender}
            performers_data.append(performer)
        return performers, performers_data
