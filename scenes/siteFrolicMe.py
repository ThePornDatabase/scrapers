import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class FrolicMeSpider(BaseSceneScraper):
    name = 'FrolicMe'
    network = 'Frolic Me'
    parent = 'Frolic Me'
    site = 'Frolic Me'

    start_urls = [
        'https://www.frolicme.com',
    ]

    title_trash = ['- film', '- Film']

    # A browser session export used to live here: an age-verification token, a
    # PHPSESSID, and a PostHog cookie carrying the device_id/distinct_id pair that
    # uniquely identifies a browser.  None of that belongs in the repo.  The
    # age_verify flow below is the supported way to get a token at runtime.
    cookies = {}


    selector_map = {
        'title': '//div[@class="entry-title"]/text()',
        # The synopsis is not always wrapped in a <span>, so requiring one left
        # every scene with an empty description.
        'description': '//div[@class="entry-content"]/p//text()',
        'date': '//script[contains(text(), "datePublished")]/text()',
        're_date': r'datePublished[\'\"]:.*?(\d{4}-\d{2}-\d{2}.*?)[\'\"]',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//span[contains(@class,"inline-flex")]//i[contains(@class, "clock")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'performers': '//span[contains(@class,"inline-flex")]/a[contains(@href, "/models/")]/text()',
        'tags': '//span[contains(@class,"inline-flex")]//i[contains(@class, "tag")]/following-sibling::a/text()',
        'external_id': r'.*\/(.*?)\/$',
        'trailer': '',
        'pagination': '/films/page/%s/?order_by=date_desc'
    }

    # ~ def start_requests(self):
        # ~ meta = {}
        # ~ meta['page'] = self.page
        # ~ yield scrapy.Request('https://www.frolicme.com', callback=self.age_verify, meta=meta, headers=self.headers, cookies=self.cookies)

    # ~ def age_verify(self, response):
        # ~ meta = response.meta
        # ~ yield scrapy.FormRequest(url="https://www.frolicme.com/wp-json/frolic/v1/verify", meta=meta, formdata={"dob": "1985-05-02", "country": "US", "search_terms": ""}, callback=self.start_requests_2)

    # ~ def start_requests_2(self, response):
        # ~ meta = response.meta

        # ~ for link in self.start_urls:
            # ~ yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//article[contains(@class, "post")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        for trash in self.title_trash:
            title = title.replace(trash, "").strip()
        return title
