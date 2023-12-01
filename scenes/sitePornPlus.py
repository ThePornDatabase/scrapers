import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkPornPlusSpider(BaseSceneScraper):
    name = 'Porn+'
    network = 'PornPlus'
    parent = 'PornPlus'

    start_url = 'https://pornplus.com'

    paginations = [
        '/series/asians-exploited',
        '/series/bbc-povd',
        '/series/bikini-splash',
        '/series/caged-sex',
        '/series/creepy-pa',
        '/series/double-trouble',
        '/series/glory-hole-4k',
        '/series/kinky-sluts-4k',
        '/series/momcum',
        '/series/property-exploits',
        '/series/rv-adventures',
        '/series/school-of-cock',
        '/series/shower-4k',
        '/series/strip-club-tryouts',
        '/series/throat-creampies',
        '/series/waxxxed',
    ]

    selector_map = {
        'title': './/a[contains(@href, "/join") and contains(@class, "text-base")]/text()',
        'description': "",
        'date': './/span[contains(@class, "text-xs") and contains(@class, "font-extra-light")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': './/video/@poster',
        'performers': './/p/a[contains(@href, "/models/")]/text()',
        'tags': "",
        'trailer': '',
        'external_id': r'/video/(.*)',
    }

    def start_requests(self):
        for pagination in self.paginations:
            url = self.start_url + pagination
            yield scrapy.Request(url, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@data-controller="video-thumbnail-video"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = super().get_title(scene)
            item['description'] = ''
            item['date'] = super().get_date(scene)
            item['image'] = scene.xpath(self.get_selector_map('image')).get()
            if "?" in item['image']:
                item['image'] = re.search(r'(.*)\?', item['image']).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = super().get_performers(scene)
            item['tags'] = []
            item['trailer'] = ''
            item['id'] = scene.xpath('./@data-vid').get()
            item['url'] = response.url
            item['site'] = scene.xpath('.//a[contains(@href, "/series/")]/img/@alt').get()
            item['parent'] = self.parent
            item['network'] = self.network
            yield self.check_item(item, self.days)
