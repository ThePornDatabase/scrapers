import re
import datetime
from dateutil.relativedelta import relativedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHDSex18Spider(BaseSceneScraper):
    name = 'HDSex18'
    network = 'HDSex18'
    parent = 'HDSex18'
    site = 'HDSex18'

    start_urls = [
        'https://hdsex18.com',
    ]

    selector_map = {
        'title': '//div[@class="main-content"]//h2[contains(@class, "title")]/text()',
        'description': '',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"data-actress")]//a/text()',
        'tags': '//div[contains(@class,"tab-info")]//a[contains(@href, "/categories/")]/text()',
        'trailer': '',
        'external_id': r'videos/(\d+)/',
        'pagination': '/videos/%s/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="thumb-video cf"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[contains(@class,"date-added")]//text()')
            if scenedate:
                scenedate = self.get_relative_date(scenedate.get())
            if scenedate:
                meta['date'] = scenedate
            else:
                meta['date'] = self.parse_date('today').isoformat()

            scene = scene.xpath('.//a[contains(@class, "video-link")]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append('18+ Teens')
        return tags

    def get_relative_date(self, datestring):
        today = datetime.datetime.now()
        datestring = datestring.lower()
        intervalcount = re.search(r'(\d{1,2})', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
        if "minute" in datestring:
            date = today - relativedelta(minutes=intervalcount)
        if "day" in datestring:
            date = today - relativedelta(days=intervalcount)
        if "today" in datestring:
            date = today
        if "yesterday" in datestring:
            date = today - relativedelta(days=1)
        if "week" in datestring:
            date = today - relativedelta(weeks=intervalcount)
        if "month" in datestring:
            date = today - relativedelta(months=intervalcount)
        if "year" in datestring:
            date = today - relativedelta(years=intervalcount)

        return date.isoformat()
