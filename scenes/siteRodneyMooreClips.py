import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteRodneyMooreClipsSpider(BaseSceneScraper):
    name = 'RodneyMooreClips'
    network = 'Rodney Moore'
    parent = 'Rodney Moore'
    site = 'Rodney Moore Clips'

    cookies = [{"domain":"rodneymoorestore.com","expirationDate":1731270263.137922,"hostOnly":true,"httpOnly":false,"name":"etoken","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"a1=4c7d32ea10e344ad388c4639d696ea072f0a697fccde25af35c5043a38ec4cbd&a2=d1927f7ca7856ddb0b2b5c38de2c311a6fb3796186660563f4c0b3dbd7e76905&a3=99470726519224"},{"domain":"rodneymoorestore.com","hostOnly":true,"httpOnly":false,"name":"use_lang","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"val=en"},{"domain":"rodneymoorestore.com","hostOnly":true,"httpOnly":false,"name":"defaults","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"{'hybridView':''}"},{"domain":"rodneymoorestore.com","expirationDate":1761593063.949509,"hostOnly":true,"httpOnly":false,"name":"ageConfirmed","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"true"}]

    start_urls = [
        'https://rodneymoorestore.com',
    ]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//div[@class="synopsis"]/p/text()',
        'date': '//span[contains(text(), "Released:")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-performer"]//span[contains(@class, "performer-name")]/span/text()',
        'tags': '//div[@class="categories"]/a/text()',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/94085/studio/rodney-moore-clips-studios.html?page=%s&media=14',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="grid-item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="release-date"]/span[contains(text(), "Length:")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[0-9a-z]+', '', duration)
            duration = re.search(r'(\d)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_performers(self, response):
        performers = super().get_performers(response)
        if not performers:
            performers = response.xpath('//a[contains(@href, "pornstars.html")]//text()')
            if performers:
                performers = performers.getall()
        return performers

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "Rodney Moore"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)

        return performers_data
