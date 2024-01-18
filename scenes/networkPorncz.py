import scrapy
import time
import datetime
import dateparser
import re


from tpdb.BaseSceneScraper import BaseSceneScraper


class PornCZSpider(BaseSceneScraper):
    name = 'PornCZ'
    network = 'PornCZ'
    parent = 'PornCZ'

    start_urls = [
        'https://www.porncz.com'
        # 'https://www.amateripremium.com',
        # 'https://www.amateursfrombohemia.com',
        # 'https://www.boysfuckmilfs.com',
        # 'https://www.chloelamour.com',
        # 'https://www.czechanalsex.com',
        # 'https://www.czechbiporn.com',
        # 'https://www.czechboobs.com',
        # 'https://www.czechdeviant.com',
        # 'https://www.czechescortgirls.com',
        # 'https://www.czechexecutor.com',
        # 'https://www.czechgaycity.com',
        # 'https://www.czechgypsies.com',
        # 'https://www.czechhitchhikers.com',
        # 'https://www.czechrealdolls.com',
        # 'https://www.czechsexcasting.com',
        # 'https://www.czechsexparty.com',
        # 'https://www.czechshemale.com',
        # 'https://www.dellaitwins.com',
        # 'https://www.dickontrip.com',
        # 'https://www.fuckingoffice.com',
        # 'https://www.fuckingstreet.com',
        # 'https://www.girlstakeaway.com',
        # 'https://www.hornydoctor.com',
        # 'https://www.hornygirlscz.com',
        # 'https://www.hunterpov.com',
        # 'https://www.ladydee.com',
        # 'https://www.publicfrombohemia.com',
        # 'https://www.retroporncz.com',
        # 'https://www.sexintaxi.com',
        # 'https://www.sexwithmuslims.com',
        # 'https://www.susanayn.com',
        # 'https://www.teenfrombohemia.com',
        # 'https://www.vrporncz.com',
    ]

    cookies = {
        'age-verified': '1',
    }

    selector_map = {
        'title': '//div[@class="heading-detail"]/h1/text()',
        'description': '//div[@class="heading-detail"]/p/text()',
        'performers': '//div[contains(text(), "Actors")]/a/text()',
        'date': '//meta[@property="video:release_date"]/@content',
        'date_formats': ['%d.%m.%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(text(), "Genres")]/a/text()',
        'duration': '//meta[@property="video:duration"]/@content',
        'external_id': r'\/(\d+)$',
        'trailer': '//meta[@property="og:video"]/@content',
        'pagination': '/en/new-videos?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="product-item-image"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//a[contains(@class, "video-detail-logo")]/img/@alt').get()
        if site:
            return site.strip().title()
        else:
            return super().get_site(response)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        date = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        return dateparser.parse(date.strip()).strftime('%Y-%m-%d')

    def get_network(self, response):
        return "Porn CZ"

    def get_parent(self, response):
        return "Porn CZ"
