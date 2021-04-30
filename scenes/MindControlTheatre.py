import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class MindControlTheatreScraper(BaseSceneScraper):
    name = 'MindControlTheatre'

    start_urls = [
        'https://mindcontroltheatre.com'
    ]

    selector_map = {
        'title': "//h1/text()",
        'description': "//div[@id='description']/p",
        'date': "//p[@id='data']/text()",
        'image': '//video/@poster',
        'performers': "//div[@id='cast']/a/text()",
        'tags': "",
        'external_id': 'movie\\/(.+)',
        'trailer': '',
        'pagination': '/movies?page=%s'
    }

    max_pages = 1

    def get_scenes(self, response):
        scenes = response.css(".movielist a::attr(href)").getall()
        for scene in scenes:
            if "movie" in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        date_string = response.xpath("//p[@id='data']/text()").extract_first()
        if date_string:
            date_string = dateparser.parse(
                date_string.split(",")[0]).isoformat()
        else:
            date_string = ""
        return date_string
