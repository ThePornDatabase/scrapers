import scrapy
import re
from datetime import datetime
import time
import datetime
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class networkAllJapanesePassPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2/text()',
        'image': '//div[@class="b-model-info-img"]/@style',
        'height': '//span[contains(text(),"Height")]/following-sibling::strong/text()',
        'birthday': '//span[contains(text(),"Birthday")]/following-sibling::strong/text()',
        'pagination': '/models/newest/all/%s',
        'external_id': 'models\/(.*).html'
    }

    name = 'AllJapanesePassPerformer'
    network = "All Japanese Pass"
    parent = "All Japanese Pass"

    start_urls = [
        'https://alljapanesepass.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href,"/model/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        return "Female"
        

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                image = re.search('url\(\'(.*.jpg)\'', image).group(1)
                if image:
                    return image.strip()
        return ''        
        

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date:
            if re.search('\d{4}-\d{2}-\d{2}', date):
                date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
                return dateparser.parse(date.strip()).isoformat()
        return ''

    def get_ethnicity(self, response):
        return "Asian"
