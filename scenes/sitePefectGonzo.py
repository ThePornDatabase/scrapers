import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'allinternal': "All Internal",
        'asstraffic': "Ass Traffic",
        'cumforcover': "All Internal",
        'fistflush': "Fist Flush",
        'givemepink': "Give Me Pink",
        'milfthing': "MILF Thing",
        'primecups': "Prime Cups",
        'purepov': "Pure POV",
        'sapphicerotica': "Sapphic Erotica",
        'spermswap': "Sperm Swap",
        'tamedteens': "Tamed Teens",
    }
    return match.get(argument, argument)


class PefectGonzoSpider(BaseSceneScraper):
    name = 'PerfectGonzo'
    network = "DEV8 Entertainment"

    date_trash = ['Released:', 'Added:', 'Published:', 'Added']

    start_urls = [
        'https://www.perfectgonzo.com',
        # 'https://www.allinternal.com',
        # 'https://www.asstraffic.com',
        # 'https://www.cumforcover.com',
        # 'https://www.milfthing.com',
        # 'https://www.primecups.com',
        # 'https://www.purepov.com',
        # 'https://www.spermswap.com',
        # 'https://www.tamedteens.com',

        'https://www.sapphix.com',
        # 'https://www.fistflush.com',
        # 'https://www.givemepink.com',
        # 'https://www.sapphicerotica.com',
    ]

    selector_map = {
        'title': '//div[@class="row"]/div/h2/text()',
        'description': '//p[@class="mg-md"]/text()',
        'date': '//span[contains(text(),"Added")]/text()',
        'image': '//video/@poster',
        'performers': '//div[@id="video-info"]//a[contains(@href,"/models/")]/text()',
        'tags': '//a[contains(@href,"tag[]")]/text()',
        'external_id': '\\/movies\\/(.*)',
        'trailer': '//video/source/@src',
        'pagination': '/movies/page-%s/?tag=&q=&model=&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="itemm"]')
        for scene in scenes:
            try:
                site = scene.xpath(
                    './/img[@class="domain-label"]/@src').get().strip()
                site = re.search(r'/img/(.*)\.com', site).group(1)
            except BaseException:
                if "sapphix" in response.url:
                    site = "Sapphix"
                else:
                    site = 'Perfect Gonzo'
            if not site:
                if "sapphix" in response.url:
                    site = "Sapphix"
                else:
                    site = 'Perfect Gonzo'
            site = match_site(site)

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': site})

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
        if not image:
            try:
                image = response.xpath(
                    '//div[@class="col-sm-12"]/a/img/@src').get()
            except BaseException:
                return ''

        return self.format_link(response, image)

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        if '/?nats' in search:
            search = re.search(r'(.*)/\?nats', search).group(1)

        return search.strip()

    def get_parent(self, response):
        if "sapphix" in response.url:
            return "Sapphix"
        return "Perfect Gonzo"

    def get_url(self, response):
        if '?nats' in response.url:
            url = re.search(r'(.*)\?nats', response.url).group(1)
        else:
            url = response.url

        return url
