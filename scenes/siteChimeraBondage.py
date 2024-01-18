import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteChimeraBondageSpider(BaseSceneScraper):
    name = 'ChimeraBondage'
    network = 'ChimeraBondage'
    parent = 'ChimeraBondage'
    site = 'ChimeraBondage'

    start_urls = [
        'https://estore.surfnetcorp.com',
    ]

    selector_map = {
        'title': '//td[@class="productheader"]/text()',
        'description': '//div[@id="productlongdesciption"]//text()',
        'date': '',
        'image': '//b[contains(text(), "Starring:")]/../following-sibling::td[1]/img/@src',
        'performers': '//b[contains(text(), "Starring:")]/following-sibling::text()[1]',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'fullid=(.*?)\&',
        'pagination': '/store/Chimerabondage/search.cfm?searchtext=&searchcategory=0&startrow=%s&sc=ReleaseDate&so=desc',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str(((int(page) - 1) * 24) + 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//td/a[contains(@href, "?fullid=")]/@title/../../a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        date_results = response.xpath('//td[@class="productdetialdata"]/text()').getall()
        for date_test in date_results:
            date_test = date_test.strip()
            date_test = re.search(r'(\d{2}-\d{2}-\d{4})', date_test)
            if date_test:
                return self.parse_date(date_test.group(1), date_formats=['%d-%m-%Y']).strftime('%Y-%m-%d')
        return ""

    def get_duration(self, response):
        duration_results = response.xpath('//td[@class="productdetialdata"]/text()').getall()
        for duration in duration_results:
            duration = duration.lower().replace("\r", "").replace("\n", "").replace("&nbsp;", "").replace(" ", "").strip()
            if "min" and "sec" in duration:
                minutes = re.search(r'(\d+)min', duration)
                if minutes:
                    minutes = int(minutes.group(1)) * 60
                else:
                    minutes = 0
                seconds = re.search(r'(\d+)sec', duration)
                if seconds:
                    seconds = int(seconds.group(1))
                else:
                    seconds = 0
                return str(minutes + seconds)

        return None

    def get_tags(self, response):
        return ['Bondage']
