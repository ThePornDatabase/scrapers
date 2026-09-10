import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLadyboysFuckedBarebackSpider(BaseSceneScraper):
    name = 'LadyboysFuckedBareback'

    start_urls = [
        'https://ladyboysfuckedbareback.com',
    ]

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://ladyboysfuckedbareback.com',
        'Referer': 'https://ladyboysfuckedbareback.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'X-NATS-cms-area-id': '126f96ec-ffdc-4f4b-a459-c9a2e78b9b67',
        'X-NATS-Entity-Decode': '1',
        'X-NATS-Natscode': 'MC4wLjE0LjE0LjAuMC4wLjAuMA',
    }
    
    cookies = [
        {"domain": "ladyboysfuckedbareback.com", "name": "consent",     "path": "/", "value": "true"},
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?section=1681&start=%s'
    }

    # Same failure as the Aziani scraper: the NATS CMS block id was hardcoded and
    # the tour has since been re-laid-out, so cms_block_id 105792 now answers
    # {"error":"cms_block_id 105792 not found"} and the crawl produced nothing
    # with no error to show for it. Every id is discovered at run time instead:
    #   <site>/natscms-app/config.json -> natsUrl + cms_area_id
    #   .../content/config             -> the pages
    #   .../content/page?slug=/videos  -> that page's layout blocks
    #   .../content/sets?cms_block_id= -> the catalogue
    app_config_url = 'https://ladyboysfuckedbareback.com/natscms-app/config.json'
    per_page = 12

    def api_headers(self, meta):
        headers = dict(self.headers or {})
        headers['X-NATS-cms-area-id'] = meta['area_id']
        return headers

    def sets_url(self, meta, page):
        start = (int(page) - 1) * self.per_page
        return (
            "%s/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1"
            "&count=%d&start=%d&cms_area_id=%s&cms_block_id=%s&orderby=published_desc"
            "&content_video_orientation=horizontal,vertical,square&content_type=video"
            "&status=enabled&text_search="
            % (meta['nats_url'], self.per_page, start, meta['area_id'], meta['block_id'])
        )

    async def start(self):
        yield scrapy.Request(self.app_config_url, callback=self.parse_app_config,
                             meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def parse_app_config(self, response):
        try:
            config = json.loads(response.text)
        except ValueError:
            print("*** LadyboysFuckedBareback: natscms-app/config.json did not parse")
            return
        meta = self.copy_meta(response)
        meta['nats_url'] = (config.get('natsUrl') or '').rstrip('/')
        meta['area_id'] = config.get('cms_area_id') or ''
        if not meta['nats_url'] or not meta['area_id']:
            print("*** LadyboysFuckedBareback: config.json carried no natsUrl/cms_area_id")
            return
        yield scrapy.Request(
            "%s/tour_api.php/content/config?cms_area_id=%s" % (meta['nats_url'], meta['area_id']),
            callback=self.parse_cms_config, meta=meta, headers=self.api_headers(meta))

    def parse_cms_config(self, response):
        try:
            pages = json.loads(response.text).get('pages') or []
        except ValueError:
            pages = []
        meta = self.copy_meta(response)
        if not any((p or {}).get('slug') == '/videos' for p in pages if isinstance(p, dict)):
            print("*** LadyboysFuckedBareback: no /videos page in the CMS config")
            return
        yield scrapy.Request(
            "%s/tour_api.php/content/page?slug=/videos" % meta['nats_url'],
            callback=self.parse_blocks, meta=meta, headers=self.api_headers(meta))

    def parse_blocks(self, response):
        meta = self.copy_meta(response)
        try:
            blocks = json.loads(response.text).get('blocks') or []
        except ValueError:
            blocks = []
        for block in blocks:
            if (block.get('settings') or {}).get('ds_source') in ('sets', 'set') and block.get('cms_block_id'):
                meta['block_id'] = block['cms_block_id']
                yield scrapy.Request(self.sets_url(meta, meta['page']), callback=self.parse,
                                     meta=meta, headers=self.api_headers(meta), dont_filter=True)
                return
        print("*** LadyboysFuckedBareback: no set-backed block on /videos")

    def parse(self, response, **kwargs):
        meta = self.copy_meta(response)
        count = 0
        for scene in self.get_scenes(response):
            count += 1
            yield scene

        if count and meta['page'] < self.limit_pages:
            meta = dict(meta)
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(self.sets_url(meta, meta['page']), callback=self.parse,
                                 meta=meta, headers=self.api_headers(meta), dont_filter=True)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        jsondata = response.json()
        scenes = jsondata['sets']
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene['name'])
            item['description'] = scene['description']
            item['date'] = scene['added_nice']

            item['performers'] = []
            item['performers_data'] = []
            if "data_types" in scene and scene['data_types']:
                for data_type in scene['data_types']:
                    if data_type['cms_data_type_id'] == "4":
                        if "data_values" in data_type and data_type['data_values']:
                            for value in data_type['data_values']:
                                item['performers'].append(value['name'])
                                perf = {}
                                perf['name'] = value['name']
                                perf['site'] = "Ladyboys Fucked Bareback"
                                perf['network'] = "Ladyboys Fucked Bareback"
                                perf['extra'] = {}
                                perf['extra']['gender'] = "Transgender Female"
                                item['performers_data'].append(perf)

            item['tags'] = []
            if "data_types" in scene and scene['data_types']:
                if "data_values" in scene['data_types'][0] and scene['data_types'][0]['data_values']:
                    for tag in scene['data_types'][0]['data_values']:
                        item['tags'].append(tag['name'])

            if "preview_formatted" in scene and scene['preview_formatted']:
                if "thumb" in scene['preview_formatted'] and scene['preview_formatted']['thumb']:
                    image = ""
                    resolution = 0
                    for thumb in scene['preview_formatted']['thumb']:
                        height = re.search(r'-(\d)', thumb)
                        if height:
                            height = int(height.group(1))
                            if height > resolution:
                                resolution = height
                                imageinfo = scene['preview_formatted']['thumb'][thumb][0]
                                item['image'] = f"https://c762d323d1.mjedge.net{imageinfo['fileuri']}?{imageinfo['signature']}"
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['id'] = scene['cms_set_id']
            item['trailer'] = ""

            # The API publishes the runtime; it was simply never read.
            item['duration'] = None
            lengths = scene.get('lengths') or {}
            if str(lengths.get('total') or '').isdigit():
                item['duration'] = str(int(lengths['total']))

            # The tour has no per-scene page (its CMS pages are /, /videos,
            # /models, /model/:slug and the legal ones), so the listing URL is
            # used. The old value was a section=1681 pagination link that no
            # longer exists and was identical for every scene on a page.
            item['url'] = "https://ladyboysfuckedbareback.com/videos"
            item['network'] = "Ladyboys Fucked Bareback"
            item['parent'] = "Ladyboys Fucked Bareback"
            item['site'] = "Ladyboys Fucked Bareback"

            yield self.check_item(item, self.days)
