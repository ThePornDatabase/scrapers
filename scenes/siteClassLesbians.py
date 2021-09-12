import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClassMediaSpider(BaseSceneScraper):
    name = 'ClassLesbians'
    network = 'Class Media'

    start_urls = [
        'https://www.class-lesbians.com/',
    ]

    selector_map = {
        'title': "//h1/text()",
        'description': "//div[@class='expand opened']/p[1]/text()",
        'date': '//span[@class="period"]/text()',
        'date_formats': ['%d.%m.%Y'],
        'performers': '//div[@class="main-info"]/p[@class="cast"]/a/text()',
        'image': '//div[@class="banner-video"]/img/@src',
        'tags': '',
        'external_id': r'.*\/(.*?)$',
        'trailer': '',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="box new-videos-box"]/a[contains(@href,"/videos/")]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Class Lesbians"

    def get_parent(self, response):
        return "Class Lesbians"
