import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class ScorePassSpider(BaseSceneScraper):
    name = 'ScorePass'
    network = 'ScorePass'

    start_urls = [
        'https://www.18eighteen.com',
        'https://www.40somethingmag.com',
        'https://www.50plusmilfs.com',
        'https://www.60plusmilfs.com',
        'https://www.autumn-jade.com',
        'https://www.bigtitangelawhite.com',
        'https://www.bigtithitomi.com',
        'https://www.bigtitterrynova.com',
        'https://www.bigtitvenera.com',
        'https://www.bootyliciousmag.com',
        'https://www.bustyangelique.com',
        'https://www.bustyarianna.com',
        'https://www.bustyinescudna.com',
        'https://www.bustykellykay.com',
        'https://www.bustykerrymarie.com',
        'https://www.bustymerilyn.com',
        'https://www.chloesworld.com',
        'https://www.christymarks.com',
        'https://www.codivorexxx.com',
        'https://www.creampieforgranny.com',
        'https://www.daylenerio.com',
        'https://www.desiraesworld.com',
        'https://www.evanottyvideos.com',
        'https://www.grannygetsafacial.com',
        # 'https://www.bigboobspov.com',
        # 'https://www.bigtithooker.com',
        # 'https://www.bonedathome.com',
    ]

    selector_map = {
        'title': "#videos_page-page h1::text",
        'description': "//meta[@itemprop='description']/@content | //*[@class='p-desc']/text()",
        'date': "//div[contains(@class, 'stat')]//span[contains(text(),'Date:')]/following-sibling::span/text()",
        'image': '//meta[@property="og:image"]/@content',
        'performers': "//div[contains(@class, 'stat')]//span[contains(text(),'Featuring:')]/following-sibling::span/a/text()",
        'tags': "",
        'external_id': 'videos\\/.+\\/(\\d+)',
        'trailer': '',
        'pagination': 'xxx-teen-videos/?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.css(".video").css('a').xpath("@href").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        if '18eighteen' in base:
            return self.format_url(base, '/xxx-teen-videos/?page=%s' % page)

        if '40somethingmag' in base:
            return self.format_url(base, '/xxx-mature-videos/?page=%s' % page)

        if '50plusmilfs' in base:
            return self.format_url(base, '/xxx-milf-videos/?page=%s' % page)

        if '60plusmilfs' in base:
            return self.format_url(base, '/xxx-granny-videos/?page=%s' % page)

        if 'bootyliciousmag' in base:
            return self.format_url(base, '/big-booty-videos/?page=%s' % page)

        if 'codivorexxx' in base:
            return self.format_url(base, '/scenes/?page=%s' % page)

        if 'creampieforgranny' in base:
            return self.format_url(
                base, '/milf-creampie-scenes/?page=%s' % page)

        if 'grannygetsafacial' in base:
            return self.format_url(
                base, '/granny-facial-scenes/?page=%s' % page)

        return self.format_url(base, '/videos/?page=%s' % page)
