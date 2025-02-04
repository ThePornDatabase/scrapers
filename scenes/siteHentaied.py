import scrapy
import re
import html
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteHentaiedSpider(BaseSceneScraper):
    name = 'Hentaied'
    network = 'Hentaied'
    parent = 'Hentaied'

    start_urls = [
        'https://hentaied.com/',
    ]

    selector_map = {
        'title': '//div[contains(@class,"shortcode-wrapper")]//script[contains(text(), "datePublished")]/text()',
        're_title': r'\"name\".*?\"(.*?)\"',
        'description': '//div[@id="fullstory"]/p//text()',
        'date': '//div[contains(@class,"shortcode-wrapper")]//script[contains(text(), "datePublished")]/text()',
        're_date': r'\"datePublished\".*?\"(.*?)\"',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//div[contains(@class, "durationandtime")]/div/text()[contains(., ":")]',
        'performers': '//div[@class="tagsmodels"]/a/text()|//img[contains(@alt, "model")]/following-sibling::div[contains(@class, "taglist")]/a/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
        'director': '//div[contains(@class, "director") and contains(@class, "tagsmodels")]//a/text()',
        'external_id': '.*\/(.*?)$',
        'trailer': '//video/source/@src',
        'pagination': '/all-videos/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Hentaied"

    def get_parent(self, response):
        return "Hentaied"


    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description).replace("&nbsp;"," ").replace("\n","")
            description = re.sub('\s{3,99}',' ', description)
            return html.unescape(description.strip())

        return ''
