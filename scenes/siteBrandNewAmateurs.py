import scrapy
import re
import dateparser
import html
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteBrandNewAmateursSpider(BaseSceneScraper):
    name = 'BrandNewAmateurs'
    network = 'Brand New Amateurs'
    parent = 'Brand New Amateurs'

    start_urls = [
        'https://www.brandnewamateurs.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href,"/categories/")]/text()',
        'external_id': '.*\/(.*?).html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        're_trailer': 'video src=\"(.*\.mp4)\"',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]//a[not(contains(@href,"signup"))]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Brand New Amateurs"
        
    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_performers(self, response):
        return []


    def get_id(self, response):
        if 'external_id' in self.regex and self.regex['external_id']:
            search = self.regex['external_id'].search(response.url)
            if search:
                return search.group(1).lower()

        return None


    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return html.unescape(description.strip())

        return ''
        

    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title')).get()
        if title:
            if ';;' in title:
                title = re.search('(.*);;', title).group(1)
            return string.capwords(html.unescape(title.strip()))
        
        else:
            return ''
    

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                trailer = "https://www.brandnewamateurs.com" + trailer
                return trailer.replace(" ", "%20")

        return ''    
