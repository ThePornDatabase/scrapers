import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class MoviesAdultDVDEmpirePerformerSpider(BasePerformerScraper):
    name = 'AdultDVDEmpireMoviePerformer'
    network = "Adult DVD Empire"

    start_url = 'https://www.adultdvdempire.com'

    paginations = [
        '/hottest-pornstars.html?sort=ag_added&page={}&fq=ag_cast_gender%3aF',
        '/hottest-pornstars.html?sort=ag_added&page={}&fq=ag_cast_gender%3aM',
        '/hottest-pornstars.html?sort=ag_added&page={}&fq=ag_cast_gender%3aT',
        # ~ '/hottest-pornstars.html?page={}&fq=ag_cast_gender%3aF',
        # ~ '/hottest-pornstars.html?page={}&fq=ag_cast_gender%3aM',
        # ~ '/hottest-pornstars.html?page={}&fq=ag_cast_gender%3aT',
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False'}

    selector_map = {
        'name': '//div[@id="content"]/section/div/div/h1/text()',
        'bio': '//div[@class="modal-body text-md"]/div/following-sibling::text()',
        'image_blob': True,
        'height': '//div[@class="modal-body text-md"]/div/ul/li[contains(text(), "Height")]/text()',
        'weight': '//div[@class="modal-body text-md"]/div/ul/li[contains(text(), "Weight")]/text()',
        'measurements': '//div[@class="modal-body text-md"]/div/ul/li[contains(text(), "Measurements")]/text()',
        'eyecolor': '//div[@class="modal-body text-md"]/div/ul/li[contains(text(), "Eyes")]/text()',
        'birthplace': '//div[@class="modal-body text-md"]/div/ul/li[contains(text(), "From:")]/text()',
        'astrology': '//div[@class="modal-body text-md"]/div/ul/li[contains(text(), "Sign:")]/text()',
        'pagination': '/en/collections/page/%s?media=video',
        'external_id': r''
    }

    def start_requests(self):
        base = self.start_url
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(base, pagination, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': pagination, 'base': base},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['base'], meta['pagination'], meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, pagination, page):
        return self.format_url(base, pagination.format(page))

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="row"]/div[contains(@class, "col-xs-6")]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)

    def get_gender(self, response):
        meta = response.meta
        if meta['pagination'][-1:] == 'F':
            return "Female"
        if meta['pagination'][-1:] == 'M':
            return "Male"
        if meta['pagination'][-1:] == 'T':
            return "Trans"
        return None

    def get_image(self, response):
        # Check for bodyshot...  also no clue why the bodyshot is labelled as headshot, but it is
        image = response.xpath('//div[@id="content"]/section/div/div/a[@label="Headshot"]/@href')
        if image:
            return self.format_link(response, image.get())
        # No body shot, check for head shot
        image = response.xpath('//div[@id="content"]/section/div/div/a/img/@src')
        if image:
            return self.format_link(response, image.get())
        return None

    def get_weight(self, response):
        weight = super().get_weight(response)
        if weight:
            weight = re.search(r':.*?(\d{2,3})', weight)
            if weight:
                weight = weight.group(1)
                weight = str(round(int(weight) * .45359237)) + "kg"
                return weight
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            height = re.search(r':.*?(\d).*?(\d{1,2})', height)
            if height:
                feet = int(height.group(1))
                inches = int(height.group(2))
                cm = round((inches + (feet * 12)) * 2.54)
                return str(cm) + "cm"
        return ''

    def get_measurements(self, response):
        measurements = super().get_measurements(response).upper()
        if measurements:
            measurements = re.search(r': (.*)$', measurements)
            if measurements:
                measurements = re.sub(r'[^A-Z0-9-]', '', measurements.group(1))
                if re.search(r'(\d{1,3}[A-J]+-\d{1,3}-\d{1,3})', measurements):
                    return re.search(r'(\d{1,3}[A-J]+-\d{1,3}-\d{1,3})', measurements).group(1)
        return None

    def get_cupsize(self, response):
        measurements = super().get_measurements(response).upper()
        if measurements:
            measurements = re.search(r': (.*)$', measurements)
            if measurements:
                measurements = re.sub(r'[^A-Z0-9-]', '', measurements.group(1))
                if re.search(r'(\d{1,3}[A-J]+-\d{1,3}-\d{1,3})', measurements):
                    return re.search(r'(\d{1,3}[A-J]+)-\d{1,3}-\d{1,3}', measurements).group(1)
        return None

    def get_eyecolor(self, response):
        eyecolor = super().get_eyecolor(response)
        if eyecolor:
            eyecolor = re.search(r': (.*)$', eyecolor)
            if eyecolor:
                return eyecolor.group(1).replace("Eyes", "").strip()
        return

    def get_birthplace(self, response):
        birthplace = super().get_birthplace(response)
        if birthplace:
            birthplace = re.search(r': (.*)$', birthplace)
            if birthplace:
                return birthplace.group(1).strip()
        return

    def get_astrology(self, response):
        astrology = super().get_astrology(response)
        if astrology:
            astrology = re.search(r': (.*)$', astrology)
            if astrology:
                return astrology.group(1).strip()
        return

    def get_bio(self, response):
        bio = self.process_xpath(response, self.get_selector_map('bio'))
        if bio:
            bio = bio.getall()
            bio = " ".join(bio).replace("  ", " ")
            return self.cleanup_text(bio)

        return ''
