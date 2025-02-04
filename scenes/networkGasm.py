import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class GasmSpider(BaseSceneScraper):
    name = 'Gasm'
    network = 'Gasm'
    parent = 'Gasm'

    selector_map = {
        'title': '//a[contains(@class,"like")]/following-sibling::span[1]/text()|//span[contains(@class,"gqTitle")]/text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//h3[@class="post_date"]/span/text()',
        'date_formats': ['%b %d, %Y'],
        'performers': '//h4[contains(text(), "Featuring")]/following-sibling::a[contains(@href, "/models/")]/text()',
        'tags': '//h4[contains(text(), "Categories")]/following-sibling::a/text()',
        'trailer': '',
        'site': '//h4[contains(text(), "Channel")]/following-sibling::a/text()',
        'external_id': r'details\/([0-9]+)',
        'pagination': '/studio/profile/harmonyvision?page=%s',
        'type': 'Scene',
    }

    sites = [
        {'profile': 'buttformation', 'site': "Buttformation"},
        {'profile': 'cosplaybabes', 'site': "Cosplay Babes"},
        {'profile': 'filthyandfisting', 'site': "Filthy and Fisting"},
        {'profile': 'funmovies', 'site': "Fun Movies"},
        {'profile': 'herzogvideos', 'site': "Herzog Video"},
        {'profile': 'hotgold', 'site': "Hot Gold"},
        {'profile': 'inflagranti', 'site': "Inflagranti"},
        {'profile': 'japanhd', 'site': "JapanHD"},
        {'profile': 'leche69gasm', 'site': "Leche 69"},
        {'profile': 'magmafilm', 'site': "Magma Film"},
        {'profile': 'mmvfilms', 'site': "MMV"},
        {'profile': 'pornxn', 'site': "Pornxn"},
        {'profile': 'theundercoverlover', 'site': "Under Cover Lover"},
        {'profile': 'harmonyvision', 'site': "HarmonyVision"},
    ]

    def get_next_page_url(self, base, page, profile):
        pagination = f"/studio/profile/{profile}?page=%s"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def start_requests(self):
        yield scrapy.Request("https://www.gasm.com", callback=self.start_requests_2, dont_filter=True)

    def start_requests_2(self, response):
        meta = {}
        meta['page'] = self.page
        for site in self.sites:
            meta['site'] = site['site']
            meta['profile'] = site['profile']
            link = 'https://www.gasm.com'
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['profile']), callback=self.parse, meta=meta, dont_filter=True)

    def parse(self, response, **kwargs):
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['profile']), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"_results_item") and contains(@class, "_results_posts_item")]/div[@class="post_item video"]/..')
        for scene in scenes:
            link = self.format_link(response, scene.xpath('./div[1]/div[@class="post_video"]/a/@href').get())
            if re.search(self.get_selector_map('external_id'), link):
                duration = scene.xpath('.//i[contains(@class, "fa-clock")]/following-sibling::b/text()')
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.get())
                image = scene.xpath('.//a/@data-media-poster')
                if image:
                    meta['image'] = self.format_link(response, image.get())
                    meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
                trailer = scene.xpath('//a/@data-xpose-mp4')
                if trailer:
                    meta['trailer'] = self.format_link(response, trailer.get())
                yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta)
