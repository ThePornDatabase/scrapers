import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteMinnanoAVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//section[contains(@class,"main-column")]/h1/span/text()',
        'image': '//section[contains(@class,"main-column")]//div[@class="act-area"]/div/img/@src',
        'image_blob': True,
        'birthday': '//section[contains(@class,"main-column")]//div[@class="act-profile"]//a[contains(@href, "birthday")]/@href',
        're_birthday': r'(\d{4}-\d{2}-\d{2})',
        'pagination': '/actress_list.php?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'MinnanoAV'
    network = 'R18'

    start_urls = [
        'https://www.minnano-av.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//h2[@class="ttl"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        measurements = response.xpath('//section[contains(@class,"main-column")]//div[@class="act-profile"]//span[contains(text(), "サイズ")]/following-sibling::p//text()')
        if measurements:
            measurements = "".join(measurements.getall()).strip()
            measurements = re.sub(r'[^a-zA-Z0-9/]', '', measurements)

            bust = re.search(r'B(\d+)', measurements)
            waist = re.search(r'W(\d+)', measurements)
            hips = re.search(r'H(\d+)', measurements)
            if re.search(r'B\d+([A-Za-z]+)', measurements):
                cup = re.search(r'B\d+([A-Za-z]+)', measurements).group(1)
            else:
                cup = ""

            if bust and waist and hips:
                bust = bust.group(1)
                bust = round(int(bust) / 2.54)
                waist = waist.group(1)
                waist = round(int(waist) / 2.54)
                hips = hips.group(1)
                hips = round(int(hips) / 2.54)
                measurements = f"{str(bust)}{str(cup).upper()}-{str(waist)}-{str(hips)}"
                if measurements:
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        measurements = response.xpath('//section[contains(@class,"main-column")]//div[@class="act-profile"]//span[contains(text(), "サイズ")]/following-sibling::p//text()')
        if measurements:
            measurements = "".join(measurements.getall()).strip()
            measurements = re.sub(r'[^a-zA-Z0-9/]', '', measurements)

            bust = re.search(r'B(\d+)', measurements)
            if re.search(r'B\d+([A-Za-z]+)', measurements):
                cup = re.search(r'B\d+([A-Za-z]+)', measurements).group(1)
            else:
                cup = ""

            if bust and cup:
                bust = bust.group(1)
                bust = round(int(bust) / 2.54)
                cup = str(bust) + cup
                return cup

        return ""

    def get_name(self, response):
        name = super().get_name(response)
        if "/" in name:
            name = re.search(r'/(.*)', name).group(1)
        name = re.sub(r'[^a-zA-Z0-9-\.\'_ ]', '', name)
        return string.capwords(name.strip())

    def get_ethnicity(self, response):
        ethnicity_test = response.xpath('//section[contains(@class,"main-column")]//div[@class="act-profile"]//span[contains(text(), "出身地")]/following-sibling::p/a/text()')
        if ethnicity_test:
            ethnicity_test = ethnicity_test.get()
            if ethnicity_test != "海外":
                return "Asian"
        return ""

    def get_height(self, response):
        height = response.xpath('//section[contains(@class,"main-column")]//div[@class="act-profile"]//span[contains(text(), "サイズ")]/following-sibling::p//text()')
        if height:
            height = "".join(height.getall()).strip()
            if re.search(r'T(\d+)', height):
                height = re.search(r'T(\d+)', height).group(1)
                return f"{height}cm"
        return ""

    def get_image(self, response):
        image = super().get_image(response)
        if "?" in image:
            image = re.search(r'(.*?)\?', image).group(1)
        return image

    def get_url(self, response):
        perfurl = super().get_url(response)
        if "?" in perfurl:
            perfurl = re.search(r'(.*?)\?', perfurl).group(1)
        return perfurl
