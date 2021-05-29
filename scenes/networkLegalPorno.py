import scrapy
from io import StringIO
from html.parser import HTMLParser
from tpdb.BaseSceneScraper import BaseSceneScraper

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()
        
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
    
class LegalPornoSpider(BaseSceneScraper):
    name = 'LegalPorno'
    network = 'Legal Porno'

    start_urls = [
        'https://www.analvids.com',
        'https://pornworld.com'
    ]

    selector_map = {
        'title': "//h1[@class='watchpage-title']",
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
        title = self.process_xpath(
            response, self.get_selector_map('title')).get().strip()
        if title:
            title = strip_tags(title).strip()
            return title
        return ''
