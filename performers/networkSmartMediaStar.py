import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SmartMediaStarPerformerSpider(BasePerformerScraper):
    name = 'SmartMediaStarPerformer'
    network = 'Smart Media Star'
    parent = 'Smart Media Star'

    start_urls = [
        'https://realitylovers.com/',
        'https://tsvirtuallovers.com'
    ]

    limit_pages = 30

    selector_map = {
        'name': '//h1[contains(@class,"girlDetails-title")]/text()',
        'image': '//img[contains(@class,"girlDetails-posterImage")]/@srcset',
        'image_blob': True,
        'bio': '//p[contains(@class,"girlDetails-bioText")]//text()',
        'birthday': '//b[contains(text(),"Birthday")]/../following-sibling::dd[1]/text()',
        'birthplace': '//b[contains(text(),"Country")]/../following-sibling::dd[1]/text()',
        'cupsize': '//b[contains(text(),"Cup")]/../following-sibling::dd[1]/text()',
        'height': '//b[contains(text(),"Height")]/../following-sibling::dd[1]/text()',
        're_height': r'[^\(]+\(([^\)]+)\)',
        'weight': '//b[contains(text(),"Weight")]/../following-sibling::dd[1]/text()',
        're_weight': r'[^\(]+\(([^\)]+)\)',
        'pagination': 'girls/page%s',
        'external_id': r'girl\/([0-9]+)\/'
    }

    site_genders = {
        'realitylovers': "Female",
        'tsvirtuallovers': "Trans"
    }

    def get_gender(self, response):
        site = super().get_site(response)
        return self.site_genders[site]

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@class,"girlsCategory-girlItem")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_image(self, response):
        image = super().get_image(response)
        image = self.get_main_image_from_srcset(image)
        return image

    @staticmethod
    def get_main_image_from_srcset(srcset):
        images = dict(map(lambda image: (image.split("%20")[1], image.split("%20")[0]), srcset.split(",")))
        for size in ['2x', '1x']:
            if size in images:
                return images[size]

        return None
