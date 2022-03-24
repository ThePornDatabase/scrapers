import re
import scrapy
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteTenshigaoSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="intro"]/div/strong[contains(text(), "Name")]/following-sibling::text()',
        'image': '//span[@class="bigroundedthumbs"]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="intro"]/p//text()',
        'haircolor': '//div[@class="intro"]/div/strong[contains(text(), "Hair")]/following-sibling::text()',
        'height': '//div[@class="intro"]/div/strong[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//div[@class="intro"]/div/strong[contains(text(), "Weight")]/following-sibling::text()',
        'birthday': '//div[@class="intro"]/div/strong[contains(text(), "Birth date")]/following-sibling::text()',
        'piercings': '//div[@class="intro"]/div/strong[contains(text(), "Piercings")]/following-sibling::text()',
        'tattoos': '//div[@class="intro"]/div/strong[contains(text(), "Tatoo")]/following-sibling::text()',
        'measurements': '//div[@class="intro"]/div/strong[contains(text(), "Body")]/following-sibling::text()',
        'cupsize': '//div[@class="intro"]/div/strong[contains(text(), "Breasts Cup")]/following-sibling::text()',
        'pagination': '/jav-models/page/%s',
        'external_id': r'model\/(.*)/'
    }

    name = 'TenshigaoPerformer'
    network = 'Tenshigao'
    parent = 'Tenshigao'
    site = 'Tenshigao'

    max_pages = 1

    start_urls = [
        'https://tenshigao.com',
    ]

    def start_requests(self):
        url = "https://tenshigao.com/jav-models/"
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelinfo"]/a[@class="block"]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_nationality(self, response):
        return "Japanese"

    def get_country(self, response):
        return "Japan"

    def get_ethnicity(self, response):
        return "Asian"

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(B\d{2,3}-W\d{2,3}-H\d{2,3})', measurements):
                bust = re.search(r'B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust) / 2.54)
                waist = re.search(r'W(\d{2,3})', measurements).group(1)
                if waist:
                    waist = round(int(waist) / 2.54)
                hips = re.search(r'H(\d{2,3})', measurements).group(1)
                if hips:
                    hips = round(int(hips) / 2.54)

                cupsize = response.xpath('//div[@class="intro"]/div/strong[contains(text(), "Breasts Cup")]/following-sibling::text()').get()
                if cupsize:
                    if cupsize == "N/A":
                        cupsize = ''
                    else:
                        if "cup size" in cupsize.lower():
                            cupsize = re.search(r'CUP SIZE (\w{1,4})', cupsize.upper()).group(1)
                        cupsize = cupsize.strip()

                if bust and waist and hips and cupsize:
                    measurements = str(bust) + cupsize + "-" + str(waist) + "-" + str(hips)
                elif bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)

                if measurements:
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(B\d{2,3}-W\d{2,3}-H\d{2,3})', measurements):
                bust = re.search(r'B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust) / 2.54)

                cupsize = response.xpath('//div[@class="intro"]/div/strong[contains(text(), "Breasts Cup")]/following-sibling::text()').get()
                if cupsize:
                    if cupsize == "N/A":
                        cupsize = ''
                    else:
                        if "cup size" in cupsize.lower():
                            cupsize = re.search(r'CUP SIZE (\w{1,4})', cupsize.upper()).group(1)
                        cupsize = cupsize.strip()

                if bust and cupsize:
                    cupsize = str(bust) + cupsize
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = "https:" + image
            return self.format_link(response, image)
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height and re.search(r'(\d+\s?cm)', height):
                    height = re.search(r'(\d+\s?cm)', height)
                    if height:
                        height = height.group(1).strip()
                        height = height.replace(" ", "")
                        return height + "cm"
                if "0 ft" not in height:
                    return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight:
                    weight = re.search(r'(\d+\s?kg)', weight)
                    if weight:
                        weight = weight.group(1).strip()
                        weight = weight.replace(" ", "")
                        return weight + "kg"
                    weight = ''
                    return weight.strip()
        return ''

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date:
            return dateparser.parse(date.strip(), date_formats=['%B %d, %Y']).isoformat()
        return ''

    def get_bio(self, response):
        bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
        bio = " ".join(bio)
        bio = bio.replace("Read More", "").replace("...", "")
        return bio

    def get_haircolor(self, response):
        haircolor = super().get_haircolor(response)
        haircolor = haircolor.replace("Hair Color", "").strip()
        return haircolor
