import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJukujoClubSpider(BaseSceneScraper):
    name = 'JukujoClub'
    network = 'Jukujo Club'
    parent = 'Jukujo Club'
    site = 'Jukujo Club'

    start_urls = [
        'https://en.jukujo-club.com',
    ]

    selector_map = {
        'title': '//div[@class="movie_info"]//dt[contains(text(), "Title:")]/following-sibling::dd[1]/text()',
        'description': '',
        'date': '//div[@class="movie_info"]//dt[contains(text(), "Upload on:")]/following-sibling::dd[1]/text()',
        'date_formats': ['%Y/%m/%d'],
        'image': '//div[@class="movie_main_box"]/div/img/@src',
        'performers': '//div[@class="movie_info"]//dt[contains(text(), "Name")]/following-sibling::dd[1]/a/text()',
        'tags': '//div[@class="movie_info"]//dt[contains(text(), "Genre:")]/following-sibling::dd[1]//a/text()',
        'duration': '//p[@class="all_tt"]/../../following-sibling::div[@class="dl_box"]/p/span[1]/text()',
        're_duration': r'(\d{1,2}:\d{1,2}:?\d{1,2}?)',
        'trailer': '',
        'external_id': r'.*/(\d+)/',
        'pagination': '/mov/?do=1&page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//span[@class="tl_thumb"]/a[contains(@href, "/mov/movie")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page):
        page = str((page - 1) * 20)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Asian" not in tags:
            tags.append("Asian")
        if "Rotor" in tags:
            tags.remove("Rotor")
            tags.append("Vibrator")
        if "Electric Massager" in tags:
            tags.remove("Electric Massager")
            tags.append("Vibrator")
        if "Famous Actress" in tags:
            tags.remove("Famous Actress")
            tags.append("Pornstar")
        if "Non-Japanese" in tags:
            tags.remove("Asian")

        return tags
