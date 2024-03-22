import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkFanCentroSpider(BaseSceneScraper):
    name = 'FanCentro'
    network = 'FanCentro'

    start_urls = [
        ['Just Lucy', True, 'justlucy94'],
        ['Mdemma', True, 'mdemma'],
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
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}

        for link in self.start_urls:
            meta['page'] = self.page
            meta['siteid'] = link[2]
            meta['site'] = link[0]
            meta['parse_performer'] = link[1]
            yield scrapy.Request(url=self.get_next_page_url(self.page, meta), callback=self.parse, meta=meta, headers=self.headers)

    def parse(self, response):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta), callback=self.parse, meta=meta, headers=self.headers)

    def get_next_page_url(self, page, meta):
        link = f"https://fancentro.com/lapi/feed?filter%5BprofileAlias%5D={meta['siteid']}&filter%5BwithInactive%5D=1&filter%5BcontentSection%5D=clip&thumbnailSizes%5Bclip.cover%5D=Ewe1mwK819%2CQYHojytoKM%2Cwv8oBuQHGy%2CAgZ4mIATPd%2CuDrXbF6zst%2CuaKV7hnDcF%2CuaKV7hnDc2&thumbnailSizes%5Bprofile.avatar%5D=wv8oBuQHGy&thumbnailSizes%5BpostResource.image%5D=uaKV7hnDc2%2CvRDNthbb3h%2CRS8qPJQXEw%2CuDrXbF6zst&fields%5Bprofiles%5D=alias%2Cavatar%2CprofileData&fields%5Bposts%5D=title%2Cbody%2CpublishDate%2CisDateHidden%2Cprice%2Cpolls%2CisPinned%2Cresources%2CpostAttachments%2CpostTags&page%5Bnumber%5D={page}&page%5Bsize%5D=10&sort=-publishDate"
        return link

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        if "included" in jsondata:
            jsondata = jsondata['included']
            cliptags = []
            for entry in jsondata:
                if entry['type'] == "clipTags":
                    cliptags.append(entry)
            for entry in jsondata:
                if entry['type'] == "clips":
                    scene = entry
                    item = SceneItem()

                    item['id'] = scene['id']
                    item['title'] = scene['attributes']['title']
                    item['description'] = scene['attributes']['description']
                    item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['attributes']['publishDate']).group(1)
                    item['duration'] = scene['attributes']['length']
                    if meta['parse_performer']:
                        item['performers'] = [meta['site']]
                    else:
                        item['performers'] = []

                    item['tags'] = []
                    if "relationships" in entry and "clipTags" in entry['relationships'] and entry['relationships']['clipTags']['data']:
                        for tag in entry['relationships']['clipTags']['data']:
                            for clipentry in cliptags:
                                if tag['id'] == clipentry['id']:
                                    item['tags'].append(clipentry['attributes']['alias'])
                                    break

                    for imagekey in scene['attributes']['coverUrl']:
                        image = imagekey
                    item['image'] = scene['attributes']['coverUrl'][image]
                    if item['image']:
                        item['image_blob'] = self.get_image_blob_from_link(item['image'])

                    item['trailer'] = ""

                    item['type'] = "Scene"
                    item['site'] = f"FanCentro: {meta['site']}"
                    item['parent'] = f"FanCentro: {meta['site']}"
                    item['network'] = "FanCentro"

                    item['url'] = f"https://fancentro.com/{meta['siteid']}/clips/{item['id']}/"

                    if item['id'] and item['title']:
                        yield self.check_item(item, self.days)
