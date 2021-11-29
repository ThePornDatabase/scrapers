import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKin8tengokuSpider(BaseSceneScraper):
    name = 'Kin8tengoku'
    network = 'Kin8tengoku'
    parent = 'Kin8tengoku'
    site = 'Kin8tengoku'

    start_urls = [
        'https://en.kin8tengoku.com',
    ]

    selector_map = {
        'title': '//div[@id="sub_main"]/p[contains(@class,"sub_title")]/text()',
        'description': '',
        'date': '//td[contains(text(), "Date")]/following-sibling::td/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//script[contains(text(), "imgurl")]/text()',
        're_image': r'imgurl.*?\'//(.*\.jpg)',
        'performers': '//td[@class="movie_table_td2"]/div/a[contains(@href, "actor")]/text()',
        'tags': '//td[@class="movie_table_td2"]/div/a[not(contains(@href, "actor"))]/text()',
        'external_id': r'.*/(\d+)/.*',
        'trailer': '//script[contains(text(), "imgurl")]/text()',
        're_trailer': r'videourl.*?\'//(.*\.mp4)',
        'pagination': '/listpages/all_%s.htm'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="movielisttext01"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = super().get_title(response)
        if title:
            if "/" in title:
                title = re.search(r'(.*)/', title).group(1)
        return title

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "4K" in tags:
            tags.remove('4K')
        if "KIN8 Original" in tags:
            tags.remove('KIN8 Original')
        if "Kin8 Original" in tags:
            tags.remove('Kin8 Original')
        if "Masterbation" in tags:
            tags.remove('Masterbation')
            tags.append('Masturbation')
        if "Costume Play" in tags:
            tags.remove('Costume Play')
            tags.append('Cosplay')
        return tags

    def get_image(self, response):
        image = super().get_image(response)
        if image:
            if "https://en.kin8tengoku.com/en.kin8tengoku.com" in image:
                image = image.replace("https://en.kin8tengoku.com/en.kin8tengoku.com", "https://en.kin8tengoku.com")
        return image

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        if trailer:
            if "https://en.kin8tengoku.com/en.kin8tengoku.com" in trailer:
                trailer = trailer.replace("https://en.kin8tengoku.com/en.kin8tengoku.com", "https://en.kin8tengoku.com")
        return trailer
