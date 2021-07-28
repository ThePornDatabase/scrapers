import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteMixedXSpider(BaseSceneScraper):
    name = 'MixedX'
    network = 'Mixed X'

    start_urls = [
        'https://mixedx.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]//h3/text()',
        'description': '//div[contains(@class, "videoDetails")]//p/text()',
        'performers': '//div[contains(@class, "featuring") and contains(., "Featuring")]//following-sibling::li/a/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href,"categories")]/text()',
        'external_id': '\/trailers\/(.*).html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        're_trailer': 'video src=\"(.*?\.mp4)',
        'pagination': '/categories/movies/%s/latest/',
    }

    def get_scenes(self, response):
        scenes = self.process_xpath(response, '//div[@class="item-thumb"]/div/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Mixed X"
   
    def get_parent(self, response):
        return "Mixed X"


    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = self.format_link(response, image)
            return image.replace("-1x.jpg","-2x.jpg")

        return None


    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return "https://mixedx.com" + trailer.replace(" ", "%20")

        return ''
