import re
import json
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAzianiSpider(BaseSceneScraper):
    name = 'Aziani'
    network = 'Aziani'
    parent = 'Aziani'
    site = 'Aziani'

    start_urls = [
        'https://aziani.com',
    ]

    cookies = {"name": "consent", "value": "true"}

    headers = {
        'X-Nats-Cms-Area-Id': "3b4c609c-6a0d-4cb9-9cce-0605f32b79ec",
        'X-Nats-Entity-Decode': 1,
        'x-nats-natscode': 'MC4wLjIuMi4wLjAuMC4wLjA',
    }

    selector_map = {
        'external_id': r'',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    # The NATS CMS block id used to be hardcoded and the tour has since been
    # re-laid-out, so cms_block_id 114458 now answers
    # {"error":"cms_block_id 114458 not found"} and the crawl produced nothing.
    # Every id is therefore discovered at run time:
    #   aziani.com/natscms-app/config.json  -> natsUrl + cms_area_id
    #   .../content/config                  -> the pages and the content server
    #   .../content/page?slug=<page>        -> that page's layout blocks
    #   .../content/sets?cms_block_id=<id>  -> the catalogue itself
    # All of the tour's video pages return the same 2000+ set catalogue, but only
    # some blocks include the Series data type -- and Series is what get_scenes
    # reads to tell Aziani, Aziani Iron, CreamPiled, 2 Poles 1 Hole and Mr Saltys
    # apart. Candidate blocks are therefore probed and the first one that returns
    # Series is used; a block without it would file every scene under "Aziani".
    app_config_url = 'https://aziani.com/natscms-app/config.json'
    page_slug_re = r'^/(videos|[a-z0-9]+-videos|2poles1hole|creampiled)$'
    per_page = 18

    def api_headers(self, meta):
        headers = dict(self.headers or {})
        headers['X-Nats-Cms-Area-Id'] = meta['area_id']
        headers['X-Nats-Entity-Decode'] = '1'
        headers['Accept'] = 'application/json'
        return headers

    def sets_url(self, meta, page):
        start = (int(page) - 1) * self.per_page
        return (
            "%s/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1"
            "&count=%d&start=%d&cms_area_id=%s&cms_block_id=%s&orderby=published_desc"
            "&content_type=video&status=enabled&text_search="
            % (meta['nats_url'], self.per_page, start, meta['area_id'], meta['block_id'])
        )

    async def start(self):
        yield scrapy.Request(self.app_config_url, callback=self.parse_app_config,
                             meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def parse_app_config(self, response):
        try:
            config = json.loads(response.text)
        except ValueError:
            print("*** Aziani: natscms-app/config.json did not parse")
            return
        meta = self.copy_meta(response)
        meta['nats_url'] = (config.get('natsUrl') or '').rstrip('/')
        meta['area_id'] = config.get('cms_area_id') or ''
        if not meta['nats_url'] or not meta['area_id']:
            print("*** Aziani: config.json carried no natsUrl/cms_area_id")
            return
        yield scrapy.Request(
            "%s/tour_api.php/content/config?cms_area_id=%s" % (meta['nats_url'], meta['area_id']),
            callback=self.parse_cms_config, meta=meta, headers=self.api_headers(meta))

    def parse_cms_config(self, response):
        try:
            config = json.loads(response.text)
        except ValueError:
            print("*** Aziani: content/config did not parse")
            return
        meta = self.copy_meta(response)
        meta['page_slugs'] = [p.get('slug') for p in config.get('pages') or []
                              if isinstance(p, dict) and re.match(self.page_slug_re, p.get('slug') or '')]
        meta['block_ids'] = []
        if not meta['page_slugs']:
            print("*** Aziani: no video pages in the CMS config")
            return
        yield self.request_page(meta)

    def request_page(self, meta):
        slug = meta['page_slugs'].pop(0)
        return scrapy.Request(
            "%s/tour_api.php/content/page?slug=%s" % (meta['nats_url'], slug),
            callback=self.parse_blocks, meta=meta, headers=self.api_headers(meta), dont_filter=True)

    def parse_blocks(self, response):
        meta = self.copy_meta(response)
        try:
            page = json.loads(response.text)
        except ValueError:
            page = {}
        for block in page.get('blocks') or []:
            source = (block.get('settings') or {}).get('ds_source')
            block_id = block.get('cms_block_id')
            if block_id and source in ('sets', 'set') and block_id not in meta['block_ids']:
                meta['block_ids'].append(block_id)
        if meta['page_slugs']:
            yield self.request_page(meta)
        elif meta['block_ids']:
            yield self.probe_block(meta)
        else:
            print("*** Aziani: no set-backed blocks found")

    def probe_block(self, meta):
        meta['block_id'] = meta['block_ids'].pop(0)
        probe = dict(meta)
        probe['probing'] = True
        return scrapy.Request(self.sets_url(probe, 1), callback=self.parse_probe,
                              meta=probe, headers=self.api_headers(meta), dont_filter=True)

    def parse_probe(self, response):
        meta = self.copy_meta(response)
        try:
            sets = json.loads(response.text).get('sets') or []
        except ValueError:
            sets = []
        has_series = any(dt.get('data_type') == 'Series'
                         for entry in sets for dt in entry.get('data_types') or [])
        if not has_series and meta['block_ids']:
            yield self.probe_block(meta)
            return
        if not sets:
            print("*** Aziani: no block returned any sets")
            return
        if not has_series:
            print("*** Aziani: no block exposed Series; sites cannot be told apart")
        meta = dict(meta)
        meta.pop('probing', None)
        meta['page'] = self.page
        yield scrapy.Request(self.sets_url(meta, meta['page']), callback=self.parse,
                             meta=meta, headers=self.api_headers(meta), dont_filter=True)

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
        scenes = json.loads(response.text)
        for scene in scenes['sets']:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['name'])
            item['id'] = scene['cms_set_id']
            item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description']))

            for thumb in scene['preview_formatted']['thumb']:
                scenethumb = thumb
            scenethumb = scene['preview_formatted']['thumb'][scenethumb][0]
            image = "https://c75c0c3063.mjedge.net" + scenethumb['fileuri'] + "?" + scenethumb['signature']
            # ~ image = "https://y2y8k2k4.ssl.hwcdn.net/" + scenethumb['fileuri'] + "?" + scenethumb['signature']
            item['image'] = image.replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*?)\?', image).group(1)
            item['trailer'] = ""

            item['date'] = scene['added_nice']

            item['url'] = f"https://aziani.com/video/{item['id']}"
            item['tags'] = []
            item['site'] = 'Aziani'
            item['performers'] = []
            directors = []
            for dataset in scene['data_types']:
                if dataset['data_type'] == 'Tags':
                    for tag in dataset['data_values']:
                        item['tags'].append(tag['name'])

                if dataset['data_type'] == 'Series':
                    if "data_values" in dataset and dataset['data_values']:
                        item['site'] = dataset['data_values'][0]['name']

                if dataset['data_type'] == 'Models' or dataset['data_type'] == 'Talent':
                    for model in dataset['data_values']:
                        item['performers'].append(model['name'])

                if dataset['data_type'] == 'Videographers':
                    for model in dataset['data_values']:
                        directors.append(model['name'])

            if directors:
                item['director'] = ",".join(directors)

            if "lengths" in scene and scene['lengths']:
                if "total" in scene['lengths'] and scene['lengths']['total']:
                    item['duration'] = scene['lengths']['total']

            item['parent'] = 'Aziani'
            item['network'] = 'Aziani'

            yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.ok:
                return req.content
        return None
