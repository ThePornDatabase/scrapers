import scrapy
import re

from tpdb.BasePerformerScraper import BasePerformerScraper


class networkWowNetworkPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//script[contains(text(), "nextItem")]/text()',
        'image': '',
        'bio': '//div[@class="archive-description"]/p/text()',
        'nationality': '//div[@class="archive-description"]/p/text()',
        'pagination': '/models/page/%s/',
        'external_id': '',
    }

    name = 'WowNetworkPerformer'
    network = "Wow Network"

    start_urls = [
        'https://www.18onlygirlsblog.com/',
        'https://www.ultrafilms.xxx/',
        'https://www.wowgirlsblog.com/',
        'https://www.wowpornblog.com/',
    ]

    def get_performers(self, response):
        performers = response.xpath('//main[contains(@class,"site-main")]//div[@class="videos-list"][1]/article[contains(@class,"thumb-block")]')
        for performer in performers:
            meta={}
            performerlink = performer.xpath('./a/@href').get()
            imagelink = performer.xpath('./a/div/picture/@data-srcset').get()
            if not imagelink:
                imagelink = performer.xpath('./a/div/img/@data-srcset').get()
            if not imagelink:
                imagelink = performer.xpath('.//img/@data-src').get()
            if not imagelink:
                imagelink = performer.xpath('.//img/@src').get()
                
            if imagelink:
                images = re.findall('(http.*?\.jpg)', imagelink)
                if images:
                    images.sort(reverse=True)
                    meta = {'image':images[0]}
            else:
                meta = {'image':''}
            yield scrapy.Request(
                url=self.format_link(response, performerlink),
                callback=self.parse_performer, meta=meta
            )

    def get_gender(self, response):
        return "Female"

    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).get().strip()
        if name:
            name = re.search('.*WebPage.*?\"name\":\"(.*?)\".*?url', name).group(1)
            if name:
                return name.strip()
                
        return ''
        
    def get_nationality(self, response):
        bio = response.xpath(self.get_selector_map('nationality')).get()
        if bio:
            bio = bio.lower()
            if "adult model from" in bio:
                nationality = re.search('adult model from (.*)', bio).group(1)
                if nationality:
                    return nationality.replace(".","").strip().title()
        return ''

    def get_image(self,response):
        return ''
