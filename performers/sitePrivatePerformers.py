import re
import os
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SitePrivatePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"pornstar-wrapper")]//h1/text()',
        'measurements': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Measurements")]/following-sibling::text()',
        'height': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Weight")]/following-sibling::text()',
        'nationality': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Nationality")]/following-sibling::text()',
        'astrology': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Sign")]/following-sibling::text()',
        'haircolor': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Hair")]/following-sibling::text()',
        'eyecolor': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Eye")]/following-sibling::text()',
        'tattoos': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Tattoos")]/following-sibling::text()',
        'piercings': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Piercings")]/following-sibling::text()',
        'bio': '//ul[contains(@class, "model-facts")]/li/div/text()',
        'pagination': '/pornstars/%s/',
        'external_id': r'models\/(.*).html'
    }
    custom_settings = {'CONCURRENT_REQUESTS': '1'}
    
    paginations = [
        '/pornstars/female/%s/',
        # '/pornstars/male/%s/',
    ]

    name = 'PrivatePerformer'
    network = 'Private'

    start_url = 'https://www.private.com'

    async def start(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            if "female" in pagination:
                meta['gender'] = "Female"
            else:
                meta['gender'] = "Male"
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta = self.copy_meta(response)
            meta['page'] = meta['page'] + 1
            link = self.get_next_page_url(response.url, meta['page'], meta['pagination'])
            print(f'NEXT PAGE: {meta["page"]}  ({link})')
            yield scrapy.Request(url=link, callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_performers(self, response):
        meta = self.copy_meta(response)
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            image_list = performer.xpath('.//img/@srcset').get()
            if image_list:
                image = max(re.findall(r'(https?://\S+)\s+(\d+)w', image_list), key=lambda x: int(x[1]))[0]
                if "na_pornstar" not in image:
                    meta['image'] = self.format_link(response, image)
                    meta['image_blob'] = ""
                    # meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
                    bare_image = re.search(r'(.*)\?', meta['image'])
                    if bare_image:
                        meta['image'] = bare_image.group(1)
                else:
                    meta['image'] = ''
                    meta['image_blob'] = ''

            performer = performer.xpath('./a/@href').get()
            if not meta['image']:
                yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)

    def get_name(self, response):
        meta = self.copy_meta(response)
        name = super().get_name(response)
        perfid = re.search(r'.*/(\d+)', response.url).group(1)
        if name and " " not in name:
            name = name + " " + perfid

        if "image" not in meta or not meta['image']:
            perf_url = f"https://theporndb.net/performer-sites/765-{name.lower().replace(' ', '-')}"
            with open("private_missing_images.txt", "a", encoding="utf-8") as f:
                f.write(f"NO IMAGE FOR PERFORMER: {name} - {response.url} - URL: {perf_url}\n")
            print(f"NO IMAGE FOR PERFORMER: {name} - {response.url} - TRYING {perf_url}")
        return name

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                cupsize = re.search(r'(?:\s+)?(.*)-.*-', measurements).group(1)
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if not height.replace("-", "").strip():
            height = ""
        if "cm" in height:
            height = re.sub('[^a-z0-9]', '', height.lower())
            height = re.search(r'(\d+cm)', height).group(1)
        return height

    def get_weight(self, response):
        weight = super().get_weight(response)
        if not weight.replace("-", "").strip():
            weight = ""
        if "kg" in weight:
            weight = re.sub('[^a-z0-9]', '', weight.lower())
            weight = re.search(r'(\d+kg)', weight).group(1)
        return weight

    def get_haircolor(self, response):
        haircolor = super().get_haircolor(response)
        if not haircolor.replace("-", "").strip():
            haircolor = ""
        return haircolor

    def get_eyecolor(self, response):
        eyecolor = super().get_eyecolor(response)
        if not eyecolor.replace("-", "").strip():
            eyecolor = ""
        return eyecolor

    def get_birthplace(self, response):
        birthplace = super().get_birthplace(response)
        if not birthplace.replace("-", "").strip():
            birthplace = ""
        return birthplace

    def get_astrology(self, response):
        astrology = super().get_astrology(response)
        if not astrology.replace("-", "").strip():
            astrology = ""
        return astrology

    def get_nationality(self, response):
        nationality = super().get_nationality(response)
        if not nationality.replace("-", "").strip():
            nationality = ""
        return nationality

    def get_tattoos(self, response):
        tattoos = super().get_tattoos(response)
        if not tattoos.replace("-", "").strip():
            tattoos = ""
        return tattoos

    def get_piercings(self, response):
        piercings = super().get_piercings(response)
        if not piercings.replace("-", "").strip():
            piercings = ""
        return piercings
