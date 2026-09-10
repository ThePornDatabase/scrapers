import scrapy
import re
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
        'image': '//link[@rel="preload" and @as="image"]/@href',
        # ~ 'image': '//picture[contains(@class, "video-cover")]/img/@src',
        'performers': "//span[contains(@class,'video-actor-list')]/a[contains(@class,'video-actor-link')]/text()",
        'tags': '//div[contains(@class,"video-tag-list")]/a[contains(@href, "categories")]/text()',
        'external_id': r'trailers/(.+)\.html',
        'trailer': '//source/@src',
        'pagination': '/categories/movies_%s_d.html'
        # 'pagination': '/categories/beauty-angels_%s_d.html'
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # ~ scenes = response.xpath("//a[contains(@class, 'title')]/@href").getall()
        scenes = response.xpath('//a[contains(@class,"thumb-video")]|//a[contains(@class,"thumb-photo")]')
        for scene in scenes:
            image = scene.xpath('.//picture/img/@data-srcset')
            if not image:
                image = scene.xpath('.//picture/img/@srcset')
            if image:
                image = image.get()
                # ~ print(image)
                image = re.search(r'(content.*?\.\w{3,4})', image).group(1)
                image = image.replace("-1x", "-2x")
                meta['orig_image'] = "https://teenmegaworld.net/" + image

            site = scene.xpath('.//span[contains(@class, "site-link")]/text()')
            if site:
                meta['site'] = site.get().strip()

            scenedate = scene.xpath('.//time/@datetime')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                if scenedate:
                    meta['date'] = scenedate.group(1)

            scenetitle = scene.xpath('.//h2/span[contains(@class, "title")]/text()')
            if scenetitle:
                meta['title'] = self.cleanup_title(scenetitle.get().strip())

            sceneurl = self.format_link(response, scene.xpath('./@href').get())
            yield scrapy.Request(url=sceneurl, callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//div[contains(@class,"video-actors-block")]/a[contains(@class,"video-site-link")]/text()').extract_first()
        return tldextract.extract(site).domain
    
    def get_id(self, response):
        id = super().get_id(response)
        return id.lower()