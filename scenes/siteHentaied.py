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
        'title': '//h1/text()',
        'description': '//div[@class="cont"]//p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="tagsmodels"]/a/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
        'external_id': '.*\/(.*?)\/$',
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
