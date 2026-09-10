import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRodneyMooreClipsSpider(BaseSceneScraper):
    name = 'RodneyMooreClips'
    network = 'Rodney Moore'
    parent = 'Rodney Moore'
    site = 'Rodney Moore Clips'

    # The previous Chrome-export cookie blob carried an etoken from Nov 2024; sending it
    # made the site bounce every scene to /?aspxerrorpath=... (an ASP.NET error page),
    # which has no title and so left item['title'] None.  Only the age gate matters.
    cookies = [{"name": "ageConfirmed", "value": "true"}]

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
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="grid-item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                # the age-gate cookie has to ride along on the scene requests too,
                # otherwise each one bounces to /AgeConfirmation and has no title
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     meta=meta, headers=self.headers, cookies=self.cookies)

    def get_duration(self, response):
        # Reads "37 mins."  The old version stripped [0-9a-z] before looking for the
        # digits, so it could never match, and (\d) would have caught only one of them.
        duration = response.xpath('//div[@class="release-date"]/span[contains(text(), "Length:")]/following-sibling::text()').get()
        if duration:
            minutes = re.search(r'(\d+)\s*min', duration, re.IGNORECASE)
            if minutes:
                return str(int(minutes.group(1)) * 60)
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
