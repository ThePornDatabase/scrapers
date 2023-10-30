import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class CzechAvSpider(BaseSceneScraper):
    name = 'CzechAv'
    network = 'Czech Casting'

    start_urls = [
        'https://czechamateurs.com',
        'https://czechbangbus.com',
        'https://czechbitch.com',
        'https://czechcabins.com',
        'https://czechcouples.com',
        'https://czechdungeon.com',
        'https://czechestrogenolit.com',
        'https://czechexperiment.com',
        'https://czechfantasy.com',
        'https://czechfirstvideo.com',
        'https://czechgame.com',
        'https://czechgangbang.com',
        'https://czechgardenparty.com',
        'https://czechharem.com',
        'https://czechhomeorgy.com',
        'https://czechlesbians.com',
        'https://czechmassage.com',
        'https://czechmegaswingers.com',
        'https://czechorgasm.com',
        'https://czechparties.com',
        'https://czechpawnshop.com',
        'https://czechpool.com',
        'https://czechsauna.com',
        'https://czechsharking.com',
        'https://czechsnooper.com',
        'https://czechsolarium.com',
        'https://czechspy.com',
        'https://czechstreets.com',
        'https://czechsupermodels.com',
        'https://czechtantra.com',
        'https://czechtaxi.com',
        'https://czechtoilets.com',
        'https://czechtwins.com',
        'https://czechwifeswap.com',
    ]

    selector_map = {
        'title': "//h2[@class='nice-title']/text()",
        'date': '//script[contains(@type, "json")]/text()',
        're_date': r'uploadDate[\'\"].*?(\d{4}-\d{2}-\d{2})',
        'description': '//script[contains(@type, "json")]/text()',
        're_description': r'description[\'\"].*?[\'\"](.*?)[\'\"]',
        'image': "//meta[@property='og:image']/@content",
        'tags': "",
        'external_id': '/tour\\/preview\\/(.+)/',
        'trailer': '',
        'pagination': '/tour/videos/page-%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class, "episode-list")]//div[contains(@class,"episode__preview")]//a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = response.xpath('//script[contains(@type, "json")]/text()')
        if tags:
            tags = re.search(r'keywords[\'\"].*?[\'\"](.*?)[\'\"]', tags.get())
            if tags:
                tags = tags.group(1)
                tags = tags.split(",")
                tags = list(map(lambda x: string.capwords(x.strip()), tags))
        return tags
