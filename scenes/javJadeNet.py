import re
import string
import scrapy
from dateutil.relativedelta import relativedelta
import datetime
from tpdb.BaseSceneScraper import BaseSceneScraper


class JAVJadeNetSpider(BaseSceneScraper):
    name = 'JAVJadeNet'
    network = 'R18'

    start_urls = [
        '',
    ]

    selector_map = {
        'title': '//section[@id="detailMain"]//h1//text()',
        'description': '',
        'date': '//div[contains(./h2/text(), "Information")]/following-sibling::dl/dt[contains(text(), "Downloadable")]/following-sibling::dd[1]/text()',
        'date_formats': ['%Y/%m/%d'],
        'image': '//div[@class="detailPackage"]/img/@src',
        'performers': '',
        'tags': '//div[contains(./h2/text(), "Information")]/following-sibling::dl/dt[contains(text(), "Related")]/following-sibling::dd[1]/a/text()',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': 'https://www.jade-net-home.com/categories/whats_new?utf8=%E2%9C%93&ps%5Brelease_date_m%5D=01&ps%5Brelease_date_y%5D=2024',
        'type': 'JAV',
    }

    def start_requests(self):
        if self.days == 20 and self.page == 1 and self.limit_pages == 1:
            current_month = datetime.datetime.now().strftime('%m')
            current_year = datetime.datetime.now().strftime('%Y')
            link = f"https://www.jade-net-home.com/categories/whats_new?utf8=%E2%9C%93&ps%5Brelease_date_m%5D={current_month}&ps%5Brelease_date_y%5D={current_year}"
            yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)
        else:
            begin = datetime.datetime(year=2004, month=4, day=1)
            now = datetime.datetime.now()
            delta = relativedelta(now, begin)
            delta = delta.months + (delta.years * 12)
            for x in range(0, delta + 1):
                target = datetime.datetime.now() - relativedelta(months=x)
                targetMonth = target.strftime('%m')
                targetYear = target.strftime('%Y')
                link = f"https://www.jade-net-home.com/categories/whats_new?utf8=%E2%9C%93&ps%5Brelease_date_m%5D={targetMonth}&ps%5Brelease_date_y%5D={targetYear}"
                yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = response.xpath('//div[contains(./h2/text(), "Information")]/following-sibling::dl/dt[contains(text(), "Productcode")]/following-sibling::dd[1]/text()')
        if sceneid:
            return sceneid.get().strip().upper()
        return None

    def get_duration(self, response):
        duration = response.xpath('//div[contains(./h2/text(), "Information")]/following-sibling::dl/dt[contains(text(), "Time")]/following-sibling::dd[1]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_site(self, response):
        site = response.xpath('//div[contains(./h2/text(), "Information")]/following-sibling::dl/dt[contains(text(), "Studios")]/following-sibling::dd[1]//text()')
        if site:
            return string.capwords(site.get().strip())
        return None

    def get_parent(self, response):
        return self.get_site(response)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            if "mbps" not in tag.lower() and "fetishism" not in tag.lower() and "tasty" not in tag.lower():
                tags2.append(tag)
            if "fetishism" in tag.lower():
                tags2.append("Fetish")
        return tags2
