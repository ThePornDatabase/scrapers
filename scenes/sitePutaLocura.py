import scrapy
import re
import datetime
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class PutaLocuraSpider(BaseSceneScraper):
    name = 'PutaLocura'
    network = 'Puta Locura'
    parent = 'Puta Locura'

    start_urls = [
        'https://www.putalocura.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[@class="description clearfix"]/p[2]/text()',
        'date': '//div[@class="released-views"]/span[1]/text()',
        'image': '//script[contains(text(), "fluidPlayer")]/text()',
        'performers': '', # They can be pulled with '//span[@class="site-name"]/text()', but halfway through the same spot becomes sites or categories instead
        'tags': '',
        'external_id': '.*\/(.*?)$',
        'trailer': '',
        'pagination': '/en?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="girls-site-box"]/var/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Puta Locura"
        
    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if "|" in title:
            title = re.search('(.*)\|', title).group(1)
            if title:
                title = title.strip()
        if title:
            return title.strip().title()
        return ''

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date = datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
            if date:
                return dateparser.parse(date.strip()).isoformat()

        return datetime.now().isoformat()


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        image = re.search('posterImage: ?\"(.*?)\"', image).group(1)
        if image:
            return self.format_link(response, image.strip())
        return ''

    def get_performers(self, response):
        return []

    def get_tags(self, response):
        return ["Spanish"]
