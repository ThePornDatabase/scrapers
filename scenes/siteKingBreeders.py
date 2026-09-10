import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKingBreedersSpider(BaseSceneScraper):
    name = 'KingBreeders'
    network = 'CarnalPlus'
    site = 'King Breeders'

    start_urls = [
        'https://kingbreeders.net',
    ]

    # The site was rebuilt on a new theme: the old #title-single / #header-inside
    # blocks are gone and their contents now live in div.video-info, which is why
    # the listing matched nothing and the scene pages left title/date/performers
    # unset.  The homepage still shows only its newest 14 episodes and has no
    # working pagination (/page/N and /episodes both re-serve page one), which is
    # the same reach the previous scraper had.
    selector_map = {
        'title': '//div[@class="video-info"]/h2/text()',
        'description': '//div[@class="video-description"]//text()',
        'date': '//div[@class="video-info"]//span[@class="time-full"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="entry"]//video/@poster',
        'performers': '//div[@class="video-info"]//div[contains(@class, "video-cast")]//span[@class="cp-name"]/text()',
        'trailer': '//div[@class="entry"]//video/source/@src',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}

        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for link in self.start_urls:
                yield scrapy.Request('https://kingbreeders.net', callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@id, "post-")]')
        for scene in scenes:
            sceneid = scene.xpath('./@id').get()
            sceneid = re.search(r'post-(\d+)', sceneid) if sceneid else None
            if not sceneid:
                continue
            meta['id'] = sceneid.group(1)

            scene = scene.xpath('.//a[contains(@class, "thumb-link")]/@href').get()

            if scene and re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "King Breeders"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data    