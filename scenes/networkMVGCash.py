import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'blackcockpassion': "Black Cock Passion",
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
        'https://blackcockpassion.com',
        'https://italianshotclub.com',
        'https://lesbiantribe.com',
        'https://myslutwifegoesblack.com',
        'https://pornlandvideos.com',
        'https://sologirlsmania.com',
        'https://vangoren.com',
    ]

    cookies = [{"name": "warn","value": "1"}]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="description"]/p//text()',
        'date': '//span[@class="date"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="starring"]/span/a/text()',
        'tags': '//div[contains(@class, "tags-list")]/a/text()',
        'external_id': r'.*\/(.*?).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "wrap")]/div[contains(@class, "thumb")]')
        site = re.search(r'https?://(?:www\.)?([^/]+)\.com/', response.url)
        if site:
            site = site.group(1)
            meta['site'] = match_site(site)
            meta['parent'] = match_site(site)
        for scene in scenes:
            date = scene.xpath('.//div[@class="date"]/text()')
            if date:
                date = date.get().strip()
                meta['date'] = self.parse_date(date).strftime('%Y-%m-%d')
            duration = scene.xpath('.//span[@class="duration"]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get().strip())
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and self.check_item(meta, self.days):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace("-1x.", "-3x.")
        return image
