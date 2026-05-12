import re

import scrapy
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class FittingRoomSpider(BaseSceneScraper):
    name = 'FittingRoom'

    start_urls = ['https://www.fitting-room.com/']

    cookies = [{
            "domain": ".fitting-room.com",
            "name": "splash_ok",
            "path": "/",
            "sameSite": "unspecified",
            "secure": false,
            "session": false,
            "storeId": "0",
            "value": "1"
        }, {
            "domain": ".fitting-room.com",
            "hostOnly": false,
            "httpOnly": true,
            "name": "fr_age_ok",
            "path": "/",
            "sameSite": "lax",
            "secure": false,
            "session": false,
            "storeId": "0",
            "value": "1"
        }
    ]

    selector_map = {
        'performers': '//div[@class="item"]/a[contains(@href, "model")]/text()',
        'tags': '//meta[@property="article:tag"]/@content',
        'external_id': r'videos\/(\d+)\/?',
        'pagination': '/videos_list.php?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=%s'

    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item premium")]')
        for scene in scenes:
            sceneurl = scene.xpath('./a/@href').get()
            yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        item = self.init_scene()
        scene_json = response.xpath('//script[contains(@type, "json")]/text()').get()
        scenedata = json.loads(scene_json)

        item['title'] = re.sub(r'\d{4}_\d+', '', scenedata['name']).strip()
        item['description'] = scenedata['description']
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedata['uploadDate']).group(1)

        item['image'] = scenedata['thumbnailUrl']
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image_blob'] = ''

        item['id'] = re.search(r'video/(\d+)/', response.url).group(1)
        item['duration'] = self.duration_to_seconds(scenedata['duration'])
        item['url'] = response.url
        item['network'] = 'Fitting Room'
        item['site'] = 'Fitting Room'
        item['parent'] = 'Fitting Room'

        item['performers'] = self.get_performers(response)

        yield self.check_item(item, self.days)
