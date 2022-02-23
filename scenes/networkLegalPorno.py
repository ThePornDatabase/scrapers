import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class LegalPornoSpider(BaseSceneScraper):
    name = 'LegalPorno'
    network = 'Legal Porno'

    start_urls = [
        'https://www.analvids.com',
        # ~ 'https://pornworld.com'  # Located in networkLegaPornoPornworld.py
    ]

    selector_map = {
        'title': "//h1[@class='watchpage-title']//text()",
        'description': '//div[@class="scene-description__row" and contains(., "Description")]//following-sibling::dd/text()',
        'date': "//span[@class='scene-description__detail']//a[1]/text()",
        'performers': "//div[@class='scene-description__row']//dd//a[contains(@href, '/model/') and not(contains(@href, 'forum'))]/text()",
        'tags': "//div[@class='scene-description__row']//dd//a[contains(@href, '/niche/')]/text()",
        'external_id': '\\/watch\\/(\\d+)',
        'trailer': '',
        'pagination': '/new-videos/%s'
    }

    def get_image(self, response):
        return response.xpath(
            '//div[@id="player"]/@style').get().split('url(')[1].split(')')[0]

    def get_site(self, response):
        return response.css('.studio-director__studio a::text').get().strip()

    def get_scenes(self, response):
        """ Returns a list of scenes
        @url https://pornworld.com/new-videos/1
        @returns requests 50 150
        """
        scenes = response.css(
            '.thumbnails .thumbnail .thumbnail-title a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_title(self, response):
        title = ''
        for part in self.process_xpath(response, self.get_selector_map('title')).getall():
            title += ' ' + part.strip()

        if title:
            title = ' '.join(title.split())
            return title

        return ''
