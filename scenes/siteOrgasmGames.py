import re
import string
import json
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOrgasmGamesSpider(BaseSceneScraper):
    name = 'OrgasmGames'
    network = 'Orgasm Games'
    parent = 'Orgasm Games'
    site = 'Orgasm Games'

    start_urls = [
        'https://orgasm.games',
    ]

    selector_map = {
        'external_id': r'.*/.*?$',
        'pagination': '/?sortby=new&page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        headers={'Content-Type': 'application/json'}

        data = {
            'query': 'query($sortby:String){d3El2B_7(pagin2ation:{sortby:$sortby}){id title description j8Wy5E_d{url}}ffhLx_Uf{u2y0Tc3w yMY0w6em}}',
            'variables': {
                'sortby': 'new'
            },
            'operationName': None
        }
        http = requests.post('https://orgasm.games/api/cQF7qfO8', headers=headers, json=data)
        scenes = json.loads(http.text)

        meta = {'scenes': scenes}
        yield scrapy.Request("https://orgasm.games/?sortby=new", callback=self.get_scenes, meta=meta)

    def get_scenes(self, response):
        scenes = response.meta['scenes']
        for scene in scenes['data']['d3El2B_7']:
            item = self.init_scene()
            item['id'] = scene['id']
            item['title'] = string.capwords(scene['title'])
            item['description'] = ""
            item['image'] = scene['j8Wy5E_d']['url']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
            item['url'] = f"https://orgasm.games/videos/{item['id']}"
            item['site'] = "Orgasm Games"
            item['parent'] = "Orgasm Games"
            item['network'] = "Orgasm Games"

            yield item
