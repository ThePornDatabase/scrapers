import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'italianshotclub': "Italians Hot Club",
        'lesbiantribe': "Lesbian Tribe",
        'myslutwifegoesblack': "My Slut Wife Goes Black",
        'pornlandvideos': "Pornland Videos",
        'sologirlsmania': "Solo Girls Mania",
        'vangoren': "Vangoren",
    }
    return match.get(argument, argument)


class NetworkMVGCashSpider(BaseSceneScraper):
    name = 'MVGCash'
    network = 'MVG Cash'

    start_urls = [
        'https://italianshotclub.com',
        'https://lesbiantribe.com',
        'https://myslutwifegoesblack.com',
        'https://pornlandvideos.com',
        'https://sologirlsmania.com',
        'https://vangoren.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//span[contains(text(),"Description")]/following-sibling::text()',
        'date': '//p[@class="date"]/text()',
        're_date': r'(\d{2}\/\d{2}\/\d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[contains(text(),"Tags:")]/following-sibling::a/text()',
        'external_id': r'.*\/(.*?).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"modelfeature")]')
        for scene in scenes:
            date = scene.xpath('.//div[contains(@class,"video_date") and contains(@class,"text-right")]/text()')
            if date:
                date = date.get().strip()
                date = dateparser.parse(date).isoformat()
            else:
                date = False
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                if date:
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})
                else:
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace("-1x.", "-3x.")
        return image

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))
