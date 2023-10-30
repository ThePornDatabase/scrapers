import scrapy
from tldextract import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


class TeenMegaWorldSpider(BaseSceneScraper):
    name = 'TeenMegaWorld'
    network = 'teenmegaworld'

    custom_settings = {'CONCURRENT_REQUESTS': '1'}

    start_urls = [
        'https://teenmegaworld.net',
        # 'http://rawcouples.com/',
        # 'http://anal-angels.com',
        # 'http://anal-beauty.com',
        # 'http://beauty4k.com',
        # 'http://beauty-angels.com',
        # 'http://creampie-angels.com',
        # 'http://dirty-coach.com',
        # 'http://dirty-doctor.com',
        # 'http://firstbgg.com',
        # 'http://fuckstudies.com',
        # 'http://gag-n-gape.com',
        # 'http://lollyhardcore.com',
        # 'http://noboring.com',
        # 'http://nubilegirlshd.com',
        # 'http://old-n-young.com',
        # 'http://soloteengirls.net',
        # 'http://teensexmania.com',
        # 'http://trickymasseur.com',
        # 'http://x-angels.com',
        # 'http://teensexmovs.com',
    ]

    selector_map = {
        'title': "//div[contains(@class,'video-heading')]/h1[@id='video-title']/text()",
        'description': "//div[@id='video-description']/p[@class='video-description-text']/text()",
        'date': "//div[contains(@class,'video-info-data')]/span[contains(@class,'video-info-date')]/text()",
        'date_formats': ['%B %d, %Y'],
        'image': '//deo-video/@poster | //video/@poster | //meta[@property="og:image"]/@content',
        'performers': "//span[contains(@class,'video-actor-list')]/a[contains(@class,'video-actor-link')]/text()",
        'tags': "//div[contains(@class,'video-tag-list')]/a[@class='video-tag-link']/text()",
        'external_id': r'trailers/(.+)\.html',
        'trailer': '//source/@src',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        # ~ scenes = response.xpath("//a[contains(@class, 'title')]/@href").getall()
        scenes = response.xpath('//h2[@class="thumb__title"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[contains(@class,"video-actors-block")]/a[contains(@class,"video-site-link")]/text()').extract_first()
        return tldextract.extract(site).domain

    def get_image(self, response):
        image = ''
        image = response.xpath('//deo-video/@poster | //video/@poster')
        if image:
            image = self.format_link(response, image.get())
        else:
            image = response.xpath('//meta[@property="og:image"]/@content')
            if image:
                image = self.format_link(response, image.get())

        if not image:
            image = super().get_image(response)
        return image
