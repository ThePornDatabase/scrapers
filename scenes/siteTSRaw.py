import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.spiders.scenes._natscms import resolve_block_id


class SiteTSRawSpider(BaseSceneScraper):
    name = 'TSRaw'
    network = 'TSRaw'
    parent = 'TSRaw'
    site = 'TSRaw'

    start_urls = [
        'https://www.tsraw.com',
    ]

    headers = {'X-NATS-cms-area-id': 'cc6bd0ac-a417-47d1-9868-7855b25986e5'}

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?section=1681&start=%s'
    }


    # cms_block_id belongs to a block in the tour's layout, so it changes whenever
    # the tour is re-laid-out -- and when it does the API answers
    # {"error":"cms_block_id ... not found"} and the spider silently yields
    # nothing. It is therefore looked up once per crawl; the literal below is only
    # the fallback used if that lookup fails, so this can only ever help.
    nats_site = 'https://www.tsraw.com'
    nats_block_fallback = '102013'

    @property
    def nats_block_id(self):
        if getattr(self, '_nats_block_id', None) is None:
            self._nats_block_id = resolve_block_id(self.nats_site, self.nats_block_fallback)
            if self._nats_block_id != self.nats_block_fallback:
                print('*** %s: cms_block_id %s -> %s' % (
                    self.name, self.nats_block_fallback, self._nats_block_id))
        return self._nats_block_id

    def get_next_page_url(self, base, page):
        index = str((int(page) - 1) * 48)
        url = f"https://nats.islanddollars.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=48&start={index}&cms_area_id=cc6bd0ac-a417-47d1-9868-7855b25986e5&cms_block_id={self.nats_block_id}&orderby=published_desc&content_type=video&status=enabled&text_search=&data_type_search=%7B%22100001%22:%22164%22%7D"
        return url

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        jsondata = response.json()
        scenes = jsondata['sets']
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.cleanup_title(scene['name'])
            item['description'] = scene['description']
            item['date'] = scene['added_nice']
            if self.check_item(item, self.days):

                item['performers'] = []
                if "data_types" in scene and scene['data_types']:
                    for entry in scene['data_types']:
                        if entry['data_type'] == "Models":
                            if "data_values" in entry and entry['data_values']:
                                for model in entry['data_values']:
                                    item['performers'].append(model['name'])

                item['tags'] = []
                if "data_types" in scene and scene['data_types']:
                    if "data_values" in scene['data_types'][0] and scene['data_types'][0]['data_values']:
                        for tag in scene['data_types'][0]['data_values']:
                            item['tags'].append(tag['name'])

                if "preview_formatted" in scene and scene['preview_formatted']:
                    if "thumb" in scene['preview_formatted'] and scene['preview_formatted']['thumb']:
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
                item['duration'] = scene['lengths']['total']
                item['trailer'] = ""
                item['url'] = f"https://www.tsraw.com/index.php?section=1681&start={str(int(meta['page']) * 48)}"
                item['network'] = "TSRaw"
                item['parent'] = "TSRaw"
                item['site'] = "TSRaw"

                yield self.check_item(item, self.days)
