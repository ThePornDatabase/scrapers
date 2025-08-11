import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornProsAPISpider(BaseSceneScraper):
    name = 'PornProsAPI'
    network = 'pornpros'

    sites = [
        "anal4k",
        "baeb",
        "bbcpie",
        "castingcouch-x",
        "cum4k",
        "exotic4k",
        "facials4k",
        "fantasyhd",
        "gayroom",
        "girlcum",
        "holed",
        "lubed",
        "mom4k",
        "momcum",
        "myveryfirsttime",
        "nannyspy",
        "passion-hd",
        "pornplus",
        "pornpros",
        "povd",
        "puremature",
        "spyfam",
        "strippers4k",
        "tiny4k",
        "wetvr",
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, site, page):
        return f"https://{site}.com/api/releases?sort=latest&page={str(page)}"

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for site in self.sites:
            meta['site'] = site
            headers = {'x-site': f'{site}.com'}
            yield scrapy.Request(url=self.get_next_page_url(site, self.page), callback=self.parse, meta=meta, headers=headers)

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
                headers = {"x-site": f"{meta['site']}.com"}
                yield scrapy.Request(url=self.get_next_page_url(meta['site'], meta['page']), callback=self.parse, headers=headers, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.json()
        for scene in scenes['items']:
            item = self.init_scene()

            item['title'] = self.cleanup_title(scene['title'])
            item['description'] = scene['description']
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['releasedAt']).group(1)

            item['image'] = scene['posterUrl']
            if "?img" in item['image']:
                item['image'] = re.search(r'(.*)\?img', item['image']).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if "actors" in scene and scene['actors']:
                item['performers'] = []
                item['performers_data'] = []
                for model in scene['actors']:
                    item['performers'].append(string.capwords(model['name']))
                    performer_extra = {}
                    performer_extra['name'] = string.capwords(model['name'])
                    performer_extra['site'] = "Porn Pros"
                    performer_extra['extra'] = {}
                    if model['gender'].lower() == "girl":
                        performer_extra['extra']['gender'] = "Female"
                    if model['gender'].lower() == "guy":
                        performer_extra['extra']['gender'] = "Male"
                    if "gender" in performer_extra['extra']:
                        item['performers_data'].append(performer_extra)

            if "tags" in scene and scene['tags']:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), scene['tags']))
            if "strippers4k" in meta['site'] or "pornplus" in meta['site']:
                item['id'] = scene['releaseId']
            else:
                item['id'] = scene['cachedSlug']
            item['url'] = f"https://{meta['site']}.com/video/{item['id']}"
            item['site'] = meta['site']
            if "sponsor" in scene and scene['sponsor']:
                if "cachedSlug" in scene['sponsor'] and scene['sponsor']['cachedSlug']:
                    item['site'] = scene['sponsor']['cachedSlug']

            if meta['site'] in ["gayroom"]:
                item['parent'] = "Gay Room"
            elif meta['site'] in ["anal4k", "bbcpie", "castingcouch-x", "cum4k", "exotic4k", "facials4k", "fantasyhd", "girlcum", "holed", "lubed", "mom4k", "myveryfirsttime", "nannyspy", "passion-hd", "povd", "puremature", "spyfam", "strippers4k", "tiny4k", "wetvr"]:
                item['parent'] = "Fuck You Cash"
            elif "pornplus" in meta['site'] or "momcum" in meta['site']:
                item['parent'] = "PornPlus"
            else:
                item['parent'] = "Porn Pros"

            item['network'] = "Porn Pros"

            submit = True
            if ("pornplus" in meta['site'] or "strippers4k" in meta['site']) and item['date'] < "2025-04-30":
                submit = False

            if submit:
                yield self.check_item(item, self.days)
