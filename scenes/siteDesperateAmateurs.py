import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper

class siteDesperateAmateursSpider(BaseSceneScraper):
    name = 'DesperateAmateurs'
    network = 'Desperate Amateurs'
    parent = 'Desperate Amateurs'

    start_urls = [
        'https://www.desperateamateurs.com'
    ]


    selector_map = {
        'title': '//div[@class="title_bar"]/comment()/following-sibling::text()',
        'description': '//div[@class="gallery_description"]/text()',
        'performers': '//td[contains(text(),"Featuring")]/following-sibling::td/a/text()',
        'date': '//td[@class="date"][1]/text()',
        're_date': '(\d{2}\/\d{2}\/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="movie_background"]/script[contains(text(),"picarr")][1]/text()',
        'tags': '//td[@class="plaintext"]/a[@class="model_category_link"]/text()',
        'trailer': '//div[@class="movie_background"]/script[contains(text(),"picarr")][1]/text()',
        'external_id': 'id=(\d+)',
        'pagination': '/fintour/category.php?id=5&page=%s&s=d&'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//span[@class="update_title"]/a/@href').getall()
        for scene in scenes:
            scene = "https://www.desperateamateurs.com/fintour/" + scene
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Desperate Amateurs"


    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return description.strip()

        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search('.*\"(.*?.jpg)\".*', image).group(1)
            if image:
                image = "https://www.desperateamateurs.com" + image
                return image.replace(" ", "%20")
        return ''
        
    def get_trailer(self, response):
        trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
        if trailer:
            trailer = re.search('.*\"(.*?.mp4)\".*', trailer).group(1)
            if trailer:
                trailer = "https://www.desperateamateurs.com" + trailer
                return trailer.replace(" ", "%20")
        return ''


    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date = re.search('(\d{2}\/\d{2}\/\d{4})', date).group(1)
            if date:
                date_formats = self.get_selector_map('date_formats') if 'date_formats' in self.get_selector_map() else None
                return dateparser.parse(date, date_formats=date_formats).isoformat()

        return ''
