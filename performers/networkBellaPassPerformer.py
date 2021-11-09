import re
import warnings
from urllib.parse import urlparse
import dateparser
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class BellaPassnPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile-details clear"]/h3/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'birthplace': '//p[@class="mb-1 mt-3"]/a/span/text()',
        'nationality': '//td/li/strong[contains(text(),"Ethnicity")]/../../following-sibling::td/text()',
        'ethnicity': '//td/li/strong[contains(text(),"Ethnicity")]/../../following-sibling::td/text()',
        'eyecolor': '//td/li/strong[contains(text(),"Eye Color")]/../../following-sibling::td/text()',
        'haircolor': '//td/li/strong[contains(text(),"Hair Color")]/../../following-sibling::td/text()',
        'height': '//td/li/strong[contains(text(),"Height")]/../../following-sibling::td/text()',
        'measurements': '//td/li/strong[contains(text(),"Stats")]/../../../td/text()',
        'tattoos': '//td/li/strong[contains(text(),"Tattoos")]/../../../td/text()',
        'piercings': '//td/li/strong[contains(text(),"Piercings")]/../../../td/text()',
        'birthday': '//td/li/strong[contains(text(),"Birthdate")]/../../following-sibling::td/text()',
        'bio': '//div[@class="profile-about"]/p/text()',
        'aliases': '//p[@data-test="p_aliases"]/text()',
        'pagination': '/models/%s/name/',
        'external_id': 'models/(.+).html$'
    }

    name = 'BellaPassPerformer'
    network = 'Bella Pass'
    parent = 'Bella Pass'

    start_urls = [
        'https://alexismonroe.com',
        'https://avadawn.com',
        'https://bellahd.com',
        'https://bellanextdoor.com',
        'https://bryci.com',
        'https://calicarter.com',
        'https://hd19.com',
        'https://hunterleigh.com',
        'https://janafox.com',
        'https://joeperv.com',
        'https://katiebanks.com',
        'https://monroelee.com',
        'https://taliashepard.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            # performer = performer.replace("//", "")
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).get()
            if ethnicity:
                if "," in ethnicity:
                    ethnicity = ethnicity.split(",")[0]
                return ethnicity.strip()
        return ''

    def get_nationality(self, response):
        if 'nationality' in self.selector_map:
            nationality = self.process_xpath(response, self.get_selector_map('nationality')).get()
            if nationality:
                if "," in nationality:
                    nationality = nationality.split(",")[1]
                else:
                    nationality = response.xpath('//td/li/strong[contains(text(),"Lives In")]/../../following-sibling::td/text()').get()
                if nationality:
                    return nationality.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                str_height = re.findall(r'(\d{1,2})', height)
                if len(str_height):
                    feet = int(str_height[0])
                    if len(str_height) > 1:
                        inches = int(str_height[1])
                    else:
                        inches = 0
                    heightcm = str(round(((feet * 12) + inches) * 2.54)) + "cm"
                    return heightcm.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace(" ", "").strip()
                measurements = re.search(r'(.*-\d{2}-\d{2})', measurements).group(1)
                if measurements:
                    cupsize = re.search(r'(.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.upper().strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace(" ", "").strip()
                measurements = re.search(r'(.*-\d{2}-\d{2})', measurements).group(1)
                if measurements:
                    return measurements.upper().strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                checkbirthday = re.search(r'(.*?)\s+(\d+).*(\d{4})', birthday)
                if checkbirthday:
                    if checkbirthday[3]:
                        if len(checkbirthday[2]) == 3:
                            tempday = checkbirthday[2]
                            tempday = tempday[1:]
                            birthday = checkbirthday[1] + " " + tempday + ", " + checkbirthday[3]
                return dateparser.parse(birthday.strip()).isoformat()
        return ''

    def get_image(self, response):
        url = urlparse(response.url)
        base = url.scheme + "://" + url.netloc
        if 'image' in self.selector_map:
            image = base + self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return image.strip()
        return ''
