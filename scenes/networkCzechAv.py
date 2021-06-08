from datetime import datetime

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
        'description': "//div[contains(@class, 'description')]/text() | //div[@class='desc-text']//p/text()",
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

    def get_performers(self, response):
        return ['Unknown Czech Performer']

    def get_date(self, response):
        return datetime.now().isoformat()
