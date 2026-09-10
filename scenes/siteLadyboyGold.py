import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.spiders.scenes._natscms import resolve_block_id
from tpdb.items import SceneItem


class SiteLadyboyGoldSpider(BaseSceneScraper):
    name = 'LadyboyGold'

    start_urls = [
        'https://ladyboygold.com',
    ]

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://ladyboygold.com',
        'Referer': 'https://ladyboygold.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'X-NATS-cms-area-id': 'cd9a5600-5cda-4ed0-b356-f62af1887d96',
        'X-NATS-Entity-Decode': '1'
    }
    
    cookies = [
        {"domain": "ladyboygold.com", "name": "consent",     "path": "/", "value": "true"},
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?section=1681&start=%s'
    }


    # cms_block_id belongs to a block in the tour's layout, so it changes whenever
    # the tour is re-laid-out -- and when it does the API answers
    # {"error":"cms_block_id ... not found"} and the spider silently yields
    # nothing. It is therefore looked up once per crawl; the literal below is only
    # the fallback used if that lookup fails, so this can only ever help.
    nats_site = 'https://www.ladyboygold.com'
    nats_block_fallback = '113623'

    @property
    def nats_block_id(self):
        if getattr(self, '_nats_block_id', None) is None:
            self._nats_block_id = resolve_block_id(self.nats_site, self.nats_block_fallback)
            if self._nats_block_id != self.nats_block_fallback:
                print('*** %s: cms_block_id %s -> %s' % (
                    self.name, self.nats_block_fallback, self._nats_block_id))
        return self._nats_block_id

    def get_next_page_url(self, base, page):
        index = str((int(page) -1) * 12)
        url = f"https://nats.islanddollars.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=12&start={index}&cms_area_id=cd9a5600-5cda-4ed0-b356-f62af1887d96&cms_block_id={self.nats_block_id}&orderby=published_desc&content_video_orientation=horizontal,vertical,square&content_type=video&status=enabled&text_search="
        return url

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count and 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta = response.meta
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(
                url=self.get_next_page_url(response.url, meta['page']),
                callback=self.parse,
                meta=meta,
                headers=self.headers,
                cookies=self.cookies,
            )

    def get_scenes(self, response):
        meta = response.meta
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
                                perf['site'] = "Ladyboy Gold"
                                perf['network'] = "Ladyboy Gold"
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
            item['url'] = f"https://ladyboygold.com/index.php?section=1681&start={str(int(meta['page']) * 48)}"
            item['network'] = "Ladyboy Gold"
            item['parent'] = "Ladyboy Gold"
            item['site'] = "Ladyboy Gold"

            yield self.check_item(item, self.days)
