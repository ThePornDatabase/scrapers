import re
import string
import scrapy
import datetime
from dateutil.relativedelta import relativedelta

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLustForBoysSpider(BaseSceneScraper):
    name = 'LustForBoys'
    network = 'Lust For Boys'
    parent = 'Lust For Boys'
    site = 'Lust For Boys'

    start_urls = [
        'https://www.lustforboys.com/videos?page=2',
    ]

    selector_map = {
        'title': '//div[contains(@class, "row item")]//h1/text()',
        'description': '//div[contains(@class, "row item")]//strong[contains(text(), "INFORMATION")]/following-sibling::text()',
        'image': '//video/@poster',
        'performers': '//div[@class="row"]/div[contains(@class, "item")]/a[contains(@href, "/models/")]/span/text()',
        'tags': '//div[contains(@class, "row item")]//div[@class="tags"]/a/text()',
        'external_id': r'.*/(.*?)_',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//main/div[@class="row"]//div[contains(@class, "item")]')
        for scene in scenes:

            scenedate = scene.xpath('.//span[@class="duration"]/text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                if re.search(r'(\w{3,4} \d{1,2}, \d{4})', scenedate):
                    scenedate = re.search(r'(\w{3,4} \d{1,2}, \d{4})', scenedate).group(1)
                    meta['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
                else:
                    meta['date'] = self.parse_date_2(scenedate)

            scene = scene.xpath('./a[1]/@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = super().get_performers(response)

        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "Lust For Boys"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)

        return performers_data

    def parse_date_2(self, datestring):
        today = datetime.datetime.now()
        datestring = re.sub(r'[^a-z0-9]+', '', datestring.lower())
        intervalcount = re.search(r'(\d+)', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
        if "today" in datestring:
            return today.strftime('%Y-%m-%d')
        days = 0
        weeks = 0
        months = 0

        if "day" in datestring:
            days = re.search(r'(\d+)day', datestring)
            if days:
                days = int(days.group(1))
            else:
                days = 0
        if "week" in datestring:
            weeks = re.search(r'(\d+)week', datestring)
            if weeks:
                weeks = int(weeks.group(1))
            else:
                weeks = 0
        if "month" in datestring:
            months = re.search(r'(\d+)month', datestring)
            if months:
                months = int(months.group(1))
            else:
                months = 0

        interval = days + (weeks * 7) + (months * 30)
        date = today - relativedelta(days=interval)
        if date:
            return date.strftime('%Y-%m-%d')
        return ""
