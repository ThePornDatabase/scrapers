import re
from urllib.parse import urlparse
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


def match_path(argument):
    match = {
        'www.mypervyfamily.com': "/meet-my-pervy-family.html?page=%s&hybridview=member",
        'www.filthykings.com': "/filthy-kings-porn-stars.html?page=%s&hybridview=member",
        'thirdworldxxx.com': "/third-world-media-porn-stars.html?page=%s&hybridview=member",
        'latinoguysporn.com': "/latino-guys-porn-stars.html?page=%s&hybridview=member",
        'www.lethalhardcore.com': "/lethal-hardcore-porn-stars.html?page=%s&hybridview=member",
        'www.wcpclub.com': "/west-coast-productions-porn-stars.html?page=%s&hybridview=member",
    }
    return match.get(argument, "")


class NetworkAdultEmpireCashPerformerSpider(BasePerformerScraper):

    selector_map = {
        'name': '//div[@id="performer"]//h1/text()',
        'image': '//div[contains(@class,"performer-page")]//picture/source[1]/@srcset',
        'ethnicity': '//ul/li[contains(text(), "Ethnicity:")]/text()',
        'eyecolor': '//ul/li[contains(text(), "Eyes:")]/text()',
        'haircolor': '//ul/li[contains(text(), "Hair:")]/text()',
        'height': '//ul/li[contains(text(), "Height:")]/text()',
        'weight': '//ul/li[contains(text(), "Weight:")]/text()',
        'measurements': '//ul/li[contains(text(), "Meas:")]/text()',
        'pagination': '?page=%s&hybridview=member',
        'external_id': r'scenes/(.*)/'
    }

    custom_settings = {'CONCURRENT_REQUESTS': '4',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'ITEM_PIPELINES': {
                           'tpdb.pipelines.TpdbApiPerformerPipeline': 400,
                       },
                       'DOWNLOADER_MIDDLEWARES': {
                           'tpdb.middlewares.TpdbPerformerDownloaderMiddleware': 543,
                       }
                       }

    name = 'AdultEmpireCashPerformer'
    network = 'AdultEmpireCash'
    parent = 'AdultEmpireCash'

    start_urls = [
        'https://www.mypervyfamily.com',
        'https://www.filthykings.com',
        'https://thirdworldxxx.com',
        'https://latinoguysporn.com',
        'https://www.lethalhardcore.com',
        'https://www.wcpclub.com',
    ]

    def get_next_page_url(self, base, page):
        url = urlparse(base)
        match_pagination = match_path(url.netloc)
        return self.format_url(base, match_pagination % page)

    def get_gender(self, response):
        if "latinoguysporn" in response.url:
            return "Male"
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//a[@class="performer"]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).get()
            if ethnicity:
                if ":" in ethnicity:
                    ethnicity = re.search(r'Ethnicity:\ (.*)', ethnicity).group(1)
                    if ethnicity:
                        return ethnicity.strip()
        return ''

    def get_eyecolor(self, response):
        if 'eyecolor' in self.selector_map:
            eyecolor = self.process_xpath(response, self.get_selector_map('eyecolor')).get()
            if eyecolor:
                if ":" in eyecolor:
                    eyecolor = re.search(r'Eyes:\ (.*)', eyecolor).group(1)
                    if eyecolor:
                        return eyecolor.strip()
        return ''

    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).get()
            if haircolor:
                if ":" in haircolor:
                    haircolor = re.search(r'Hair:\ (.*)', haircolor).group(1)
                    if haircolor:
                        return haircolor.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if ":" in height:
                    height = re.search(r'Height:\ (.*)', height).group(1)
                    if height:
                        str_height = height.replace(".", "")
                        str_height = re.search(r'(\d).*(\d{1,2})', str_height)
                        feet = int(str_height.group(1))
                        inches = int(str_height.group(2))
                        height = str(round(((feet * 12) + inches) * 2.54)) + "cm"
                        return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if ":" in weight:
                    weight = re.search(r'Weight:\ (.*)', weight).group(1)
                    if weight:
                        return weight.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                if ":" in measurements:
                    measurements = re.search(r'Meas:\ (.*)', measurements).group(1)
                    if measurements:
                        return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                if "-" in measurements:
                    cupsize = re.search(r'Meas:\ (.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.strip()
        return ''
