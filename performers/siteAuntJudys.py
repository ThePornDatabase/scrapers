import scrapy
import re
import string
from tpdb.BasePerformerScraper import BasePerformerScraper

class siteAuntJudysPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title_bar"]/span/text()',
        'image': '//div[@class="cell_top cell_thumb"]/img/@src0_2x',
        'height': '//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(.,"Height")]',
        'cupsize': '//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(.,"Bust")]',
        'measurements': '//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(.,"Measurements")]',
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': 'models\/(.*)\/'
    }

    custom_settings = {'CONCURRENT_REQUESTS': 1}

    name = 'AuntJudysPerformer'
    network = "Aunt Judys"

    start_urls = [
        # 'https://www.auntjudys.com',
        'https://www.auntjudysxxx.com',
    ]

    def get_gender(self, response):
        return 'Female'
    
    def get_network(self, response):
        site = re.search(r'https?://(www\.)?(auntjudys[a-z0-9]*?)\.', response.url)
        if site:
            site = site.group(2)
            site = site.replace("auntjudys","Aunt Judys ")
            return string.capwords(site.strip())
        return "Aunt Judys"
    
    def get_name(self, response):
        name = super().get_name(response)
        if "auntjudys.com" in response.url:
            perf_id = re.search(r'-(\w+\d{2,4})\.', response.url)
            if perf_id:
                perf_id = perf_id.group(1)
            else:
                perf_id = "999"
        elif "auntjudysxxx.com" in response.url:
            perf_id = re.search(r'-(\d+)\.', response.url)
            if perf_id:
                perf_id = perf_id.group(1)
            else:
                perf_id = "998"
        if " " not in name:
            name = string.capwords(f"{name} {perf_id}")
        return name.strip()
            
    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_url(self, response):
        return response.url

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).getall()
            if height:
                height = " ".join(height)
                if "Height:" in height:
                    height = height.replace("&nbsp;", "").replace("\n", "").replace("\t", " ").replace("\r", " ").strip()
                    height = re.sub(r"\s\s+", " ", height).strip()
                    height = re.search(r'Height:\s+(\d+.*)', height).group(1)
                    if height:
                        height = height.replace(" ","")
                        return height.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).getall()
            if measurements:
                measurements = " ".join(measurements)
                if "Measurements:" in measurements and re.search('(\d+\w+-\d+\d+)', measurements):
                    measurements = measurements.replace("&nbsp;", "").replace("\n", "").replace("\t", " ").replace("\r", " ").strip()
                    measurements = re.sub(r"\s\s+", " ", measurements).strip()
                    measurements = re.search(r'Measurements:\s+(\d+.*)', measurements).group(1)
                    if measurements:
                        measurements = re.sub('[^a-zA-Z0-9-]', '', measurements)
                        return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).getall()
            if cupsize:
                cupsize = " ".join(cupsize)
                if "Bust:" in cupsize:
                    cupsize = cupsize.replace("&nbsp;", "").replace("\n", "").replace("\t", " ").replace("\r", " ").strip()
                    cupsize = re.sub(r"\s\s+", " ", cupsize).strip()
                    cupsize = re.search(r'Bust:\s+(\d+.*)', cupsize).group(1)
                    if cupsize:
                        cupsize = cupsize.replace(" ","")
                        return cupsize.strip()
        return ''
        
    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if not image:
                image = response.xpath('//div[@class="cell_top cell_thumb"]/img/@src0_2x').get()
            if not image:
                image = response.xpath('//div[@class="cell_top cell_thumb"]/img/@src').get()
            if image:
                image = self.format_link(response, image)
                return image.strip()
        return ''        
