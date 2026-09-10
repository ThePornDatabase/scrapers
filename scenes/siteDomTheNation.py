import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class DomTheNationSpider(BaseSceneScraper):
    name = 'DomTheNation'
    network = 'DerangedDollars'
    parent = 'DerangedDollars'

    start_urls = [
        'https://www.domthenation.com'
    ]

    selector_map = {
        'title': '',
        'description': '//div[contains(@class,"feat-top-body")]/p/text()',
        'date': '',
        'image': '//a[@class="feat-top-media"]/img/@src',
        'performers': '//p[@class="update-info text-center feat-top-info"]/a[contains(@href,"/sub/")]/text()',
        'tags': '//p[@class="text-center feat-top-body tags"]/a/text()',
        'external_id': '\\/(\\d+)$',
        'trailer': '',
        'pagination': '/?updates/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class,"mas-update")]/a[contains(@href,"/post/movie/") or contains(@href,"/post/clip/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        """Return an ISO date, not the site's "July 8, 2026" wording.

        check_item compares item['date'] to today as a *string*, so an unparsed
        date like "July 8, 2026" sorts above "2026-09-08" and every scene was
        silently dropped as future-dated -- a crawl fetched all its scene pages and
        produced nothing, with no error.
        """
        date = response.xpath('//p[@class="update-info text-center feat-top-info"]/text()').get()
        if not date:
            return None
        date = date.strip()
        if "|" in date:
            found = re.search(r'^(.*\d{4})\s', date)
            if found:
                date = found.group(1).strip()
        scenedate = self.parse_date(date, date_formats=['%B %d, %Y', '%b %d, %Y'])
        return scenedate.strftime('%Y-%m-%d') if scenedate else None

    def get_title(self, response):
        title = response.xpath('//div[@class="row"]//h1/text()').get().strip()
        if "MOVIE:" in title:
            title = title.replace("MOVIE: ", "")
        if "CLIP:" in title:
            title = title.replace("CLIP: ", "")
        return title
