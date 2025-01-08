import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class networkGlobeTwatters(BaseSceneScraper):
    name = 'GlobeTwatter'
    network = 'Globe Twatters'
    parent = 'Globe Twatters'

    start_urls = [
        'https://asiansexdiary.com',
        'https://eurosexdiary.com',
        'https://trikepatrol.com',
        'https://tuktukpatrol.com',
        'https://milftrip.com',
        'https://helloladyboy.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[@class="cntr"]/div[contains(@class, "artl-cnt")]//p|a/text()',
        'date': '//i[@class="fa fa-calendar-o"]/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@id="myOverlay"]/amp-img/@src',
        'performers': '//div[@class="update-info"]//a[contains(@href, "/model/")]/text()',
        'tags': '//div[@class="amp-category"]/span/a/text()',
        'external_id': r'.*/(.*?)/$',
        'trailer': '//div[contains(@class, "video-player")]/amp-video/@src',
        'pagination': ['/category/conquests/page/%s/','/all-updates/page/%s/'],
        'duration': '//i[contains(@class,"fa") and contains(@class,"fa-video-camera")]/ancestor::div[1]/text()',
    }

    pattern = re.compile(r'\b[\w\s?]*\s?\b')

    def get_scenes(self, response):
        scenes = response.xpath('//article/a/@href').getall()

        meta = response.meta
        site = response.xpath('//div[contains(@class,"amp-logo-footer")]//a/@title').get()
        site = re.match(r'\b[\w\s?]*\s?\b',site).group(0).strip()
        meta['site'] = site

        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,meta=meta)

    def get_description(self, response):
        description = super().get_description(response)
        description = re.sub('<[^<]+?>', '', description).strip()
        return description
    
    def get_site(self, response):
        return response.meta['site']
    
    def get_next_page_url(self, base, page):
        if "diary" in base:
            return self.format_url(base, self.get_selector_map('pagination')[0] % page)
        else:
            return self.format_url(base, self.get_selector_map('pagination')[1] % page)
