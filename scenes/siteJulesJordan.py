import re
import scrapy
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'girlgirl': "Girl Girl",
        'julesjordan': "Jules Jordan",
        'manuelferrara': "Manuel Ferrara",
        'theassfactory': "The Ass Factory",
        'spermswallowers': "Sperm Swallowers",
    }
    return match.get(argument, argument)


class JulesJordanSpider(BaseSceneScraper):
    name = 'JulesJordan'
    network = 'julesjordan'

    start_urls = [
        'https://www.julesjordan.com',
        'https://www.manuelferrara.com',
        'https://www.theassfactory.com',
        'https://www.spermswallowers.com',
        'https://www.girlgirl.com'
    ]

    selector_map = {
        'title': '//span[@class="title_bar_hilite"]/text()|//div[@class="movie_title"]/text()',
        'description': '//span[@class="update_description"]/text()|//span[contains(text(), "Description")]/following-sibling::text()',
        'date': '//div[@class="cell update_date"]/text()|//span[contains(text(), "Date")]/following-sibling::text()',
        'performers': '//div[@class="backgroundcolor_info"]/span[@class="update_models"]/a/text() | //div[@class="gallery_info"]//span[@class="update_models"]/div[@class="container"]/a/text()|//span[contains(text(), "Starring")]/following-sibling::span[@class="update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()|//span[@class="player-scene-description"]/a[contains(@href, "/categories/")]/text()',
        'external_id': r'trial/scenes/(.+)\.html',
        'trailer': '',
        'pagination': '/trial/categories/movies_%s_d.html'
    }

    max_pages = 47

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="category_listing_wrapper_updates"]//a[1]/@href|//div[@class="grid-item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_image(self, response):
        result = re.search('useimage = "(.+?)";', response.text)
        if result:
            return self.format_link(response, result.group(1))
        else:
            result = response.xpath('//video/@poster')
            if result:
                return self.format_link(response, result.get())

    def get_site(self, response):
        site = tldextract.extract(response.url).domain
        site = match_site(site)
        return site
