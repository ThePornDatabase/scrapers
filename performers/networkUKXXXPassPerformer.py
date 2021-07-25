import scrapy
import re
import tldextract
from urllib.parse import urlparse

from tpdb.BasePerformerScraper import BasePerformerScraper


class networkUKXXXPassPerformerSpider(BasePerformerScraper):
    name = 'UKXXXPassPerformer'
    network = 'UK XXX Pass'

    start_urls = [
        'https://ukpornparty.xxx',
        'https://sexyukpornstars.xxx',
        'https://splatbukkake.xxx',
    ]

    selector_map = {
        'name': '//div[@class="updatesBlock"]/h2/text()',
        'image': '//comment()[contains(.,"Model Thumbnail")]/following-sibling::img/@src0_3x',
        'height': '//div[@class="modelbiofields"]//p[contains(text(),"Height")]/text()',
        'haircolor': '//div[@class="modelbiofields"]//p[contains(text(),"Hair")]/text()',
        'cupsize': '//div[@class="modelbiofields"]//p[contains(text(),"Bust")]/text()',
        'ethnicity': '//div[@class="modelbiofields"]//p[contains(text(),"Ethnicity")]/text()',
        'bio': '//comment()[contains(.,"Bio Extra") and not(contains(.,"Fields"))]/following-sibling::text()',
        'pagination': '/models/models_%s_d.html',
        'external_id': 'models\/(.*).html'
    }

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"model")]/a[contains(@href,"/models/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_2x').get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_1x').get()
            
        if image:
            uri = urlparse(response.url)
            base = uri.scheme + "://" + uri.netloc
            image = base + image.strip().replace(" ","%20")
            return image

        return None

    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).get()
            if haircolor:
                haircolor = haircolor.replace("&nbsp;","").replace("\n","").replace("\d","")
                haircolor = re.search('Colour:.*?([a-zA-Z].*)\s{2}',haircolor)
                if haircolor:
                    haircolor = haircolor.group(1)
                    return haircolor.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                height = height.replace("&nbsp;","").replace("\n","").replace("\d","")
                height = re.search('Height:.*?([0-9].*\")',height)
                if height:
                    height = height.group(1)
                    return height.strip()
        return ''
        
    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).get()
            if ethnicity:
                ethnicity = ethnicity.replace("&nbsp;","").replace("\n","").replace("\d","")
                ethnicity = re.search('Ethnicity:.*?([0-9].*\")',ethnicity)
                if ethnicity:
                    ethnicity = ethnicity.group(1)
                    return ethnicity.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                bust = re.search('(\d{2,3}\s?[a-z-A-Z]{1,5}?)',cupsize)
                if not bust:
                    bust = cupsize.replace("&nbsp;","").replace("\n","").replace("\d","")
                    bust = re.search('Bust:.*?([a-zA-Z].*)\s',bust)
                if bust:
                    bust = bust.group(1)
                    return bust.strip()
        return ''        
        
    def get_name(self, response):
        name =  self.process_xpath(response, self.get_selector_map('name')).get().strip()
        name = name.replace("/","").strip()
        return name
