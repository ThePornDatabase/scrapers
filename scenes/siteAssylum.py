import re
from urllib.parse import urlparse
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AssylumSpider(BaseSceneScraper):
    name = 'Assylum'
    network = 'DerangedDollars'

    start_urls = [
        'https://www.assylum.com'
    ]

    selector_map = {
        'title': '//h3[@class="mas_title"]/text()',
        'description': '//p[@class="mas_longdescription"]/text()',
        'date': '//div[@class="lch"]//comment()/following-sibling::text()',
        'image': '//div[@class="mainpic"]/comment()',
        'performers': '',
        'tags': '//p[@class="tags"]/a/text()',
        'external_id': '(\\d+)$',
        'trailer': '',
        'pagination': '/show.php?a=65_%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="item"]/a[@class="itemimg"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()

        if not image:
            image = response.xpath(
                '//div[@class="mainpic"]/img/@src').get().strip()

        if "src" in image:
            image = re.search('src=\"(.*?)\"\\ ', image).group(1).strip()

        return self.format_link(response, image)

    def get_domain(self, response):
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain

    def get_performers(self, response):
        performers = response.xpath(
            '//span[contains(@class,"lc_info mas_description")]/text()').get().strip()
        performers = performers.split(",")
        performers = list(filter(None, performers))
        temp_performers = []
        for performer in performers:
            temppointer = 0
            performer = performer.strip()

            if "Patient: " in performer:
                performer = performer.replace('Patient: ', '')
            if "Patients: " in performer:
                performer = performer.replace('Patients: ', '')
            if "Nurse: " in performer:
                performer = performer.replace('Nurse: ', '')
            if " (4K trailer available)" in performer:
                performer = performer.replace(' (4K trailer available)', '')
            if " (1hr 45min)" in performer:
                performer = performer.replace(' (1hr 45min)', '')
            if " Returns" in performer:
                performer = performer.replace(' Returns', '')
            if "Order Of The Red Star: " in performer:
                performer = performer.replace('Order Of The Red Star: ', '')
            if '(' in performer or ')' in performer:
                performer = re.sub('[\\(\\)]+', '', performer)
            if 'year-old' in performer.lower():
                performer = re.sub(
                    '\\d{2}\\ year-old\\ ', '', performer.lower())
                performer = performer.title()
            if " and " in performer.lower():
                additions = performer.lower().split(' and ')
                for addition in additions:
                    if not re.search('[^A-Za-z0-9 ]+', addition):
                        temp_performers.append(addition.title().strip())
                        temppointer = 1
            if " & " in performer.lower():
                additions = performer.lower().split(' & ')
                for addition in additions:
                    if not re.search('[^A-Za-z0-9 ]+', addition):
                        temp_performers.append(addition.title().strip())
                        temppointer = 1
            if "/" in performer.lower():
                additions = performer.lower().split('/')
                for addition in additions:
                    if not re.search('[^A-Za-z0-9 ]+', addition):
                        temp_performers.append(addition.title().strip())
                        temppointer = 1
            if " with " in performer.lower():
                additions = performer.lower().split(' with ')
                for addition in additions:
                    if not re.search('[^A-Za-z0-9 ]+', addition):
                        temp_performers.append(addition.title())
                        temppointer = 1
            if not temppointer:
                temp_performers.append(performer.title().strip())

        performers = temp_performers
        for performer in performers:
            matches = [
                "Downloadable",
                "School",
                "Offer",
                "My Only Joys",
                "The Gang",
                "P2"]
            if re.search('[^A-Za-z ]+',
                         performer) or any(x in performer for x in matches):
                performers.remove(performer)

        return list(map(lambda x: x.strip(), performers))

    def get_trailer(self, response):
        image = response.xpath(
            '//script[contains(text(),"mp4")]').get().strip()
        image = self.get_domain(
            response) + re.search('src:\\s+\'(.*)\'', image).group(1).strip()
        return image
