import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

class siteLetsDoeItPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[contains(@class,"poster-item")]/img/@data-src',
        'nationality': '//div[contains(@class,"list-item") and contains(text(),"Nationality")]/span/text()',
        'birthday': '//div[contains(@class,"list-item") and contains(text(),"Birth Date")]/span/text()',
        'birthplace': '//div[contains(@class,"list-item") and contains(text(),"Birth Place")]/span/text()',
        'fakeboobs': '//div[contains(@class,"list-item") and contains(text(),"Tits Type")]/span/text()',
        'bio': '//*[contains(@class,"read-even-more")]//text()',
        'external_id': 'models\/(.*).html'
    }

    paginations = [
        ['https://letsdoeit.com','/pornstars/sex/girls.en.html?order=activity&page=%s','Female'],
        ['https://letsdoeit.com','/pornstars/sex/guys.en.html?page=%s&order=activity','Male'],
        ['https://amateureuro.com','/pornstars/sex/girls.en.html?order=activity&page=%s','Female'],
        ['https://amateureuro.com','/pornstars/sex/guys.en.html?page=%s&order=activity','Male'],
        ['https://mamacitaz.com','/pornstars/sex/girls.en.html?order=activity&page=%s','Female'],
        ['https://mamacitaz.com','/pornstars/sex/guys.en.html?page=%s&order=activity','Male'],
        ['https://vipsexvault.com','/pornstars/sex/girls.en.html?order=activity&page=%s','Female'],
        ['https://vipsexvault.com','/pornstars/sex/guys.en.html?page=%s&order=activity','Male'],
        ['https://transbella.com','/pornstars/sex/trans.en.html?order=activity&page=%s','Trans'],
        ['https://transbella.com','/pornstars/sex/girls.en.html?page=%s&order=activity','Female'],
        ['https://transbella.com','/pornstars/sex/guys.en.html?page=%s&order=activity','Male'],
        ['https://dirtycosplay.com','/pornstars/sex/girls.en.html?page=%s&order=activity','Female'],
        ['https://dirtycosplay.com','/pornstars/sex/guys.en.html?page=%s&order=activity','Male'],
    ]

    name = 'LetsDoeItPerformer'
    network = "LetsDoeIt"

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(pagination[0], self.page, pagination[1]),
                                 callback=self.parse,
                                 meta={
                'page': self.page, 'url': pagination[0], 'pagination': pagination[1], 'gender': pagination[2]},
                headers=self.headers,
                cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
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
                        yield scrapy.Request(url=self.get_next_page_url(meta['url'], meta['page'], meta['pagination']),
                                             callback=self.parse,
                                             meta=meta,
                                             headers=self.headers,
                                             cookies=self.cookies)


    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="global-actor-card"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta=meta
            )

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                birthday = dateparser.parse(birthday.strip(), date_formats=['%b %d, %Y']).isoformat()
                return birthday
        return ''

    def get_fakeboobs(self, response):
        if 'fakeboobs' in self.selector_map:
            fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).get()
            if fakeboobs:
                fakeboobs = fakeboobs.lower()
                if "natural" in fakeboobs:
                    return "No"
                if "enhanced" in fakeboobs:
                    return "Yes"
                return fakeboobs.strip()
        return ''
        

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
            if bio:
                bio = " ".join(bio)
                bio = bio.replace("  "," ")
                return bio.strip()
        return ''        
