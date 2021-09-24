import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBoundHoneysPerformerSpider(BasePerformerScraper):
    name = 'BoundHoneysPerformer'
    network = 'Bound Honeys'

    start_urls = {
        'http://boundhoneys.com',
    }

    selector_map = {
        'name': '//div[@class="modelDetailText"]/h1/text()',
        'image': '//div[@class="modelDetailPhoto"]/img/@src',
        'bio': '//div[@class="modelDetailText"]//p[1]/text()',
        'eyecolor': '//div[@class="modelDetailText"]//p[1]/text()',
        'haircolor': '//div[@class="modelDetailText"]//p[1]/text()',
        'height': '//div[@class="modelDetailText"]//p[1]/text()',
        'weight': '//div[@class="modelDetailText"]//p[1]/text()',
        'measurements': '//div[@class="modelDetailText"]//p[1]/text()',
        'cupsize': '//div[@class="modelDetailText"]//p[1]/text()',
        'pagination': '',
        'external_id': r'model\/(.*)/'
    }

    def start_requests(self):
        url = "http://boundhoneys.com/bondage-girls.php"
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelBox"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'gender': 'Female'}
            )

    def get_image(self, response):
        image = super().get_image(response)
        image = self.format_link(response, image.strip())
        return image

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio_text = ''
            bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
            if bio:
                for bio_line in bio:
                    if ": " not in bio_line:
                        bio_line = re.sub('<[^<]+?>', '', bio_line.strip())
                        bio_line = bio_line.replace("\n", "").replace("\r", "").replace("\t", "")
                        bio_text = bio_text + bio_line
                return bio_text.strip()
        return ''

    def get_eyecolor(self, response):
        text = ''
        if 'eyecolor' in self.selector_map:
            statlines = self.process_xpath(response, self.get_selector_map('eyecolor')).getall()
            if statlines:
                for line in statlines:
                    line = line.lower()
                    if "eye colour: " in line:
                        text = re.search(r': (.*)', text)
                        if text:
                            return text.group(1).title().strip()
        return ''

    def get_haircolor(self, response):
        text = ''
        if 'haircolor' in self.selector_map:
            statlines = self.process_xpath(response, self.get_selector_map('haircolor')).getall()
            if statlines:
                for line in statlines:
                    line = line.lower()
                    if "hair: " in line:
                        text = re.search(r': (.*)', text)
                        if text:
                            text = text.group(1)
                            text = re.sub(r'\/.*', '', text)
                            return text.title().strip()
        return ''

    def get_height(self, response):
        text = ''
        if 'height' in self.selector_map:
            statlines = self.process_xpath(response, self.get_selector_map('height')).getall()
            if statlines:
                for line in statlines:
                    line = line.lower()
                    if "height: " in line:
                        text = re.search(r'(\d{3} ?cm)', line)
                        if text:
                            text = text.group(1).replace(" ", "")
                            return text.strip()
        return ''

    def get_weight(self, response):
        text = ''
        if 'weight' in self.selector_map:
            statlines = self.process_xpath(response, self.get_selector_map('weight')).getall()
            if statlines:
                for line in statlines:
                    line = line.lower()
                    if "weight: " in line:
                        text = re.search(r'(\d{2,3} ?kg)', line)
                        if text:
                            text = text.group(1).replace(" ", "")
                            return text.strip()
        return ''

    def get_cupsize(self, response):
        line = ''
        text = ''
        if 'cupsize' in self.selector_map:
            statlines = self.process_xpath(response, self.get_selector_map('cupsize')).getall()
            if statlines:
                for line in statlines:
                    line = line.lower()
                    if "bust:" in line:
                        text = re.search(r': (.*)', line)
                        if text:
                            text = re.sub(r'[^a-zA-Z0-9]', '', text.group(1))
                            return text.strip().upper()
        return ''

    def get_measurements(self, response):
        line = ''
        bust = ''
        waist = ''
        hips = ''
        if 'measurements' in self.selector_map:
            statlines = self.process_xpath(response, self.get_selector_map('measurements')).getall()
            if statlines:
                for line in statlines:
                    line = line.lower()
                    if "bust:" in line:
                        bust = re.search(r'(\d{2,3})', line).group(1)
                    if "waist:" in line:
                        waist = re.search(r'(\d{2,3})', line).group(1)
                    if "hips:" in line:
                        hips = re.search(r'(\d{2,3})', line).group(1)
                if bust and waist and hips:
                    measurements = bust + "-" + waist + "-" + hips
                    return measurements
        return ''
