import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteStrapLezzSpider(BaseSceneScraper):
    name = 'StrapLezz'
    network = 'Strap Lezz'
    parent = 'Strap Lezz'

    start_urls = [
        'https://straplezz.com/',
    ]

    selector_map = {
        'title': '//h1[@class="card-title"]/text()',
        'description': '//i[contains(@class,"fa-calendar-alt")]/../../following-sibling::p/text()',
        'date': '//i[contains(@class,"fa-calendar-alt")]/following-sibling::text()',
        'image': '//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_4x',
        'performers': '//div[contains(@class,"card model")]/a/h3/text()',
        'tags': '//li[contains(@class,"tag")]/a/text()',
        'external_id': 'updates\/(.*).html',
        'trailer': '//comment()[contains(.,"Link to Trailer")]/following-sibling::a/@onclick',
        're_trailer': 'tload\(\'(.*.mp4)\'',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href,"/updates/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Strap Lezz"
        

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date = date.replace('Posted on', '').strip()
            return dateparser.parse(date, date_formats=['%B %d, %Y']).isoformat()

        return None


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_3x').get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_2x').get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_1x').get()
            
        if image:
            image = self.format_link(response, image)
            return image.replace(" ", "%20")

        return None


    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return "https://straplezz.com" + trailer.replace(" ", "%20")

        return ''
