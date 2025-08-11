import re
import string
import scrapy
from datetime import datetime, timedelta

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteExclusiveTeenPornPerformerSpider(BasePerformerScraper):
    selector_map = {
        'image': '//table[@class="maindata"]//div[@class="modelinfo"]/img/@src',
        'image_blob': True,
        'bio': '//table[@class="maindata"]//img[contains(@src, "short-information")]//ancestor::table[1]//div[contains(@style, "margin-top: 20px")]/text()',
        'birthplace': '//table[@class="maindata"]//img[contains(@src, "short-information")]//ancestor::table[1]//text()[contains(., "COUNTRY:")]/following-sibling::a[1]/text()',
        'nationality': '//table[@class="maindata"]//img[contains(@src, "short-information")]//ancestor::table[1]//text()[contains(., "COUNTRY:")]/following-sibling::a[1]/text()',
        'eyecolor': '//table[@class="maindata"]//img[contains(@src, "short-information")]//ancestor::table[1]//text()[contains(., "EYE COLOR:")]/following-sibling::a[1]/text()',
        'haircolor': '//table[@class="maindata"]//img[contains(@src, "short-information")]//ancestor::table[1]//text()[contains(., "HAIR COLOR:")]/following-sibling::a[1]/text()',

        'pagination': '/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'ExclusiveTeenPornPerformer'
    network = 'Exclusive Teen Porn'

    start_urls = [
        'https://exclusiveteenporn.com',
    ]

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination') % page
        if page == 1:
            return "https://exclusiveteenporn.com/models.html"
        return self.format_url(base, pagination)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//table[@class="cover"]//td[@class="modelcoverinfo"]/a[contains(@href, "model_")][1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_name(self, response):
        name = response.xpath('//table[@class="maindata"]//text()[contains(., "NAME:")]/following-sibling::a[1]/text()').get()
        perf_id = re.search(r'.*_(\d+)', response.url).group(1)
        return string.capwords(f"{name.strip()} {perf_id}")

    def get_birthday(self, response):
        ref_date = response.xpath('//table[@class="maindata"]//img[contains(@src, "short-information")]//ancestor::table[1]//text()[contains(., "ADDED:")]/following-sibling::a[1]/text()')
        if ref_date:
            ref_date = ref_date.get()
            ref_date = re.search(r'(\d{4}-\d{2}-\d{2})', ref_date)
            if ref_date:
                ref_date = ref_date.group(1)

        age = response.xpath('//table[@class="maindata"]//img[contains(@src, "short-information")]//ancestor::table[1]//text()[contains(., "AGE:")]/following-sibling::a[1]/text()')
        if age:
            age = age.get()
            age = re.search(r'(\d+)', age)
            if age:
                age = age.group(1)

        if age and ref_date:
            ref_date = datetime.strptime(ref_date, "%Y-%m-%d")
            birth_year = ref_date.year - int(age)
            birthdate = ref_date.replace(year=birth_year)
            return birthdate.strftime("%Y-%m-%d")
        return None
