import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.spiders.scenes._natscms import resolve_block_id
from tpdb.items import SceneItem


class SiteLatinaRawSpider(BaseSceneScraper):
    name = 'LatinaRaw'
    network = 'LatinaRaw'
    parent = 'LatinaRaw'
    site = 'LatinaRaw'

    start_urls = [
        'https://latinaraw.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': 'https://nats.islanddollars.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=24&start=%s&cms_area_id=63f59eaf-5755-425a-90f5-739014e485f0&cms_block_id=101628&orderby=published_desc&content_type=video&status=enabled',
        'type': 'Scene',
    }


    # cms_block_id belongs to a block in the tour's layout, so it changes whenever
    # the tour is re-laid-out -- and when it does the API answers
    # {"error":"cms_block_id ... not found"} and the spider silently yields
    # nothing. It is therefore looked up once per crawl; the literal below is only
    # the fallback used if that lookup fails, so this can only ever help.
    nats_site = 'https://www.latinaraw.com'
    nats_block_fallback = '101628'

    @property
    def nats_block_id(self):
        if getattr(self, '_nats_block_id', None) is None:
            self._nats_block_id = resolve_block_id(self.nats_site, self.nats_block_fallback)
            if self._nats_block_id != self.nats_block_fallback:
                print('*** %s: cms_block_id %s -> %s' % (
                    self.name, self.nats_block_fallback, self._nats_block_id))
        return self._nats_block_id

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 24)
        pagination = self.get_selector_map('pagination').replace(
            'cms_block_id=101628', 'cms_block_id=' + self.nats_block_id)
        return pagination % page

    async def start(self):
        # meta = {}
        # meta['page'] = 1
        # headers = {
        #     'Accept': 'application/json, text/plain, */*',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'en-US,en;q=0.9',
        #     'Origin': 'https://latinaraw.com',
        #     'Referer': 'https://latinaraw.com/',
        #     'X-Nats-Cms-Area-Id': '2',
        #     'X-Nats-Entity-Decode': '1',
        # }
        # link = 'https://idsandbox.hostednats.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=100&start=0&cms_area_id=2&cms_block_id=100695&orderby=published_desc&content_type=video&status=enabled&text_search=&data_type_search=%7B%22100001%22:%22163%22%7D'
        url = "https://www.latinaraw.com/videos"
        yield scrapy.Request(url, callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = 1
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://latinaraw.com',
            'Referer': 'https://latinaraw.com/',
            'X-Nats-Cms-Area-Id': '63f59eaf-5755-425a-90f5-739014e485f0',
            'X-Nats-Entity-Decode': '1',
        }

        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        jsondata = response.json()
        jsondata = jsondata['sets']

        for scene in jsondata:
            item = SceneItem()
            item['id'] = scene['cms_set_id']
            title = scene['name']
            title = title.replace(" 4k", "").replace(" 4K", "").strip()
            item['title'] = self.cleanup_title(title)
            item['description'] = self.cleanup_description(scene['description'])
            item['performers'] = []
            for performer in scene['data_types']:
                if 'data_type' in performer and performer['data_type'] and performer['data_type'] == 'Models':
                    for perf_row in performer['data_values']:
                        item['performers'].append(perf_row['name'])

            item['site'] = "LatinaRaw"
            item['network'] = "LatinaRaw"
            item['parent'] = "LatinaRaw"
            item['url'] = "https://latinaraw.com/videos/" + item['id']
            item['date'] = scene['added_nice']
            item['duration'] = scene['lengths']['total']
            item['trailer'] = ''
            item['tags'] = []
            for tags in scene['data_types']:
                if 'data_type' in tags and tags['data_type'] and tags['data_type'] == 'Category':
                    for tag in tags['data_values']:
                        item['tags'].append(tag['name'])
            
            base_url = "https://c762d323d1.mjedge.net"
            thumbs = scene['preview_formatted']['thumb']
            t = thumbs[max(thumbs, key=lambda k: int(k.split('-')[0]) * int(k.split('-')[1]))][0]
            image_url = f"{base_url}{t['fileuri']}?{t['signature']}"
            
            item['image'] = image_url
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            yield self.check_item(item, self.days)
