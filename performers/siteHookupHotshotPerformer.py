import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class HookupHotshotPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[contains(text(),"About")]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'bio': '//div[@class="profile-about"]/p/text()',
        'pagination': '/models/%s/latest/?g=',
        'external_id': r'models\/(.*).html'
    }

    name = 'HookupHotshotPerformer'
    network = "Hookup Hotshot"
    parent = "Hookup Hotshot"

    start_urls = [
        'https://hookuphotshot.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                image = image.replace(" ", "%20")
                image = image.replace("https//", "https://")
                image = image.replace("http//", "http://")
                if "https://" not in image:
                    image = "https://hookuphotshot.com" + image
                return image.strip()
            else:
                return ''

    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).get().strip()
        name = name.replace("About", "")
        return name.strip()

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).get()

            if bio:
                if "Lorem ipsum" in bio:
                    return ''
                return bio.strip()
        return ''
