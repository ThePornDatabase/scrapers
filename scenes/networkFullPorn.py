import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from datetime import date


class FullPornNetworkSpider(BaseSceneScraper):
    name = 'FullPorn'
    network = 'fullpornnetwork'

    start_urls = [
        'https://analized.com',
        'https://jamesdeen.com',
        'https://twistedvisual.com',
        'https://onlyprince.com',
        'https://baddaddypov.com',
        'https://povperverts.net',
        'https://yourmomdoesporn.com',
        'https://yourmomdoesanal.com',
        'https://dtfsluts.com',
        'https://twistedvisual.com',
        'https://teenageanalsluts.com',
        'https://pervertgallery.com',
        'https://homemadeanalwhores.com',
        'https://hergape.com',
        'https://analviolation.com',
        'https://analbbc.com',
        'https://girlfaction.com',
    ]

    selector_map = {
        'title': "//h4[contains(@class, 'text-center')]/text()",
        'description': "//p[contains(@class, 'hide-for-small-only')]/text()",
        'performers': "//div[@class='small-12'][2]//p[1]//a/text()",
        'tags': "",
        'external_id': 'scene/([A-Za-z0-9-_]+)/?',
        'trailer': '',
        'pagination': '/1/scenes/recent/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[contains(@class, 'section-updates')]//div[contains(@class, 'scene-update')]")
        for scene in scenes:
            meta = {
                'image': scene.css('img::attr(src)').get(),
            }
            url = self.format_link(
                response, scene.css('a::attr(href)').get() + '/')
            yield scrapy.Request(url=url, meta=meta, callback=self.parse_scene)

    def get_date(self, response):
        return date.today().isoformat()
