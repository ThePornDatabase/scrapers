import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteFirstAnalQuestPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="page-header"]/h3[@class="title"]/strong/text()',
        'image': '//div[@class="model-box"]/img/@src',
        'bio': '//div[@class="model-biography"]/p/text()',
        'haircolor': '//span[contains(text(), "Hair")]/following-sibling::span/text()',
        'eyecolor': '//span[contains(text(), "Eye")]/following-sibling::span/text()',
        'nationality': '//span[contains(text(), "Nationality")]/following-sibling::img/@alt',
        'measurements': '//span[contains(text(), "Measurements")]/following-sibling::span/text()',
        'birthday': '//span[contains(text(), "Birth date")]/following-sibling::span/text()',
        'pagination': '/models/%s/?sort_by=date',
        'external_id': r'model/(.*)/'
    }

    name = 'FirstAnalQuestPerformer'
    network = 'First Anal Quest'

    start_urls = [
        'http://www.firstanalquest.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="thumb-content"]/a[contains(@href, "/models/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    measurements = re.sub('[^a-zA-Z0-9-]', '', measurements)
                    return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if cupsize:
                cupsize = re.search(r'(\d+\w+)-\d+-\d+', cupsize)
                if cupsize:
                    cupsize = cupsize.group(1)
                    return cupsize.strip().upper()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = "https:" + image
            return self.format_link(response, image)
        return ''

    def get_bio(self, response):
        bio = super().get_bio(response)
        if "there is no description" in bio:
            bio = ''
        return bio

    def get_birthday(self, response):
        birthday = super().get_birthday(response)
        if birthday:
            birthday = self.parse_date(birthday, date_formats=['%d %B, %Y']).isoformat()
        return birthday
