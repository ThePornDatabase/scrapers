import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSexyMommaSpider(BaseSceneScraper):
    name = 'SexyMomma'
    network = 'Sexy Momma'
    parent = 'Sexy Momma'
    site = 'Sexy Momma'

    start_urls = [
        'https://www.sexymomma.com',
    ]

    cookies = {'_warning_page': '1'}

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[@class="detail-text"]/text()',
        'date': '',
        'image': '//script[contains(text(), "jwplayer")]/text()',
        're_image': r'.*\'(?://)?(.*?\.jpg).*',
        'performers': '',
        'tags': '',
        'external_id': r'id=(\d+)',
        'trailer': '',
        'pagination': '/moms/%s/#enter'
    }

    def start_requests(self):
        url = "https://www.sexymomma.com/moms"
        yield scrapy.Request(url, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@id="latest"]//div[contains(@class, "box-design")]')
        for scene in scenes:
            date = scene.xpath('.//strong[contains(text(), "Date")]/following-sibling::text()')
            if date:
                date = date.get()
                date = self.parse_date(date, date_formats=['%b %d, %Y']).isoformat()
            else:
                date = self.parse_date('today').isoformat()
            scene = "https://www.sexymomma.com/moms/" + scene.xpath('.//div[@class="img-div"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(scene, callback=self.parse_scene, headers={'Referer': 'https://www.sexymomma.com/moms/'}, cookies=self.cookies, meta={'date': date, 'dont_redirect': True})

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        image = re.search(self.get_selector_map('re_image'), image).group(1)
        image = "https://" + image
        return image

    def get_tags(self, response):
        return ['Family Roleplay']
