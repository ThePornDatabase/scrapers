import re
import dateparser
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteLASublimeSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/a/text()',
        'image': '',
        'bio': '//p[@class="lead"]/following-sibling::text()',
        'birthday': '//p[@class="lead"]/following-sibling::ul/li/strong[contains(text(),"Age:")]/following-sibling::text()',
        'astrology': '//p[@class="lead"]/following-sibling::ul/li/strong[contains(text(),"Sign:")]/following-sibling::text()',
        'haircolor': '//p[@class="lead"]/following-sibling::ul/li/strong[contains(text(),"Hair")]/following-sibling::text()',
        'eyecolor': '//p[@class="lead"]/following-sibling::ul/li/strong[contains(text(),"Eyes")]/following-sibling::text()',
        'tattoos': '//p[@class="lead"]/following-sibling::ul/li/strong[contains(text(),"Tattoos:")]/following-sibling::text()',
        'height': '//p[@class="lead"]/following-sibling::ul/li/strong[contains(text(),"Height:")]/following-sibling::text()',
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': r'model\/(.*)/'
    }

    name = 'LASublimePerformer'
    network = 'MVG Cash'
    start_urls = [
        'https://tours.lasublimexxx.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="single-carousel-scene"]')
        for performer in performers:
            image = performer.xpath('./a/img/@src0_3x')
            if image:
                image = image.get()
                if image:
                    image = re.search(r'.*(\/tour.*?\.jpg).*', image)
                    if image:
                        image = image.group(1)
                        image = "https://tours.lasublimexxx.com" + image.strip()
            if not image:
                image = ''
            performer = performer.xpath('./a/@href').get()
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'image': image}
            )

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            if "cm" in height:
                return height
            height = float(height.replace(",", ".")) * 100
            height = str(int(height)) + "cm"
            return height
        return ''

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
            if bio:
                return "".join(bio).strip()
        return ''

    def get_birthday(self, response):
        birthday = super().get_birthday(response)
        if birthday:
            birthday = dateparser.parse(birthday, date_formats=['%d/%m/%Y']).isoformat()
            return birthday
        return ''
