import scrapy
from scrapy.utils.project import get_project_settings
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class LegalPornoSpider(BaseSceneScraper):
    name = 'LegalPorno'
    network = 'Legal Porno'

    settings = get_project_settings()
    proxy_address = settings.get('PROXY_ADDRESS')

    start_urls = [
        'https://www.analvids.com',
        # ~ 'https://pornworld.com'  # Located in networkLegaPornoPornworld.py
    ]

    selector_map = {
        'title': "//h1[@class='watchpage-title']//text()",
        'description': '//div[@class="scene-description__row" and contains(., "Description")]//following-sibling::dd/text()',
        'date': "//span[@class='scene-description__detail']//a[1]/text()",
        'performers': "//h1[@class='watchpage-title']/a[contains(@href, '/model/')]/text()|//div[@class='scene-description__row']//dd//a[contains(@href, '/model/') and not(contains(@href, 'forum'))]/text()",
        'tags': "//div[@class='scene-description__row']//dd//a[contains(@href, '/niche/')]/text()",
        'duration': "//i[@class='fa fa-clock-o']/following-sibling::text()",
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
        meta = response.meta
        """ Returns a list of scenes
        @url https://pornworld.com/new-videos/1
        @returns requests 50 150
        """
        scenes = response.css(
            '.thumbnails .thumbnail .thumbnail-title a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = ''
        for part in self.process_xpath(response, self.get_selector_map('title')).getall():
            title += ' ' + part.strip()

        if title:
            title = ' '.join(title.split())
            return title

        return ''

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response).replace("\r", "").replace("\n", "").replace("\t", "").strip()
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob(response)
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['markers'] = self.get_markers(response)
        item['id'] = self.get_id(response)
        item['duration'] = self.get_duration(response)
        item['trailer'] = self.get_trailer(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = 'Legal Porno'

        if "bang bros" not in item['site'].lower() and "jeffsmodels" not in item['site'].lower() and "antoniosuleiman" not in item['site'].lower():
            yield self.check_item(item, self.days)
