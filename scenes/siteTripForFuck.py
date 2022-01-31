import re
import datetime
import dateparser
from dateutil.relativedelta import relativedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Spider(BaseSceneScraper):
    name = 'TripForFuck'
    network = 'Trip For Fuck'
    parent = 'Trip For Fuck'
    site = 'Trip For Fuck'

    start_urls = [
        'https://www.tripforfuck.com',
    ]

    selector_map = {
        'title': '//div[@class="container"]/h1/text()',
        'description': '//div[@class="container"]/p/text()',
        'date': '',
        'image': '//video/@poster',
        'image_blob': True,
        'performers': '//div[@class="container"]/div[@class="d-flex"]//a[contains(@href, "actor")]/text()',
        'tags': '//div[contains(@class, "search-tags")]/a/text()',
        'external_id': r'movie/(.*?)/',
        'trailer': '',
        'pagination': '/member/movie/list/index.html?page=%s&is_paginate=1'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="movie-list__item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        datestring = response.xpath('//div[contains(@class, "movie-status")]/p/text()')
        if datestring:
            datestring = datestring.get().strip().replace(",", "")
            today = datetime.datetime.now()
            datestring = datestring.lower()
            intervalcount = re.search(r'(\d+)', datestring).group(1)
            if not intervalcount:
                intervalcount = 0
            else:
                intervalcount = int(intervalcount)
            if "minute" in datestring:
                scenedate = today - relativedelta(minutes=intervalcount)
            if "hour" in datestring:
                scenedate = today - relativedelta(hours=intervalcount)
            if "day" in datestring:
                scenedate = today - relativedelta(days=intervalcount)
            if "today" in datestring:
                scenedate = today
            if "yesterday" in datestring:
                scenedate = today - relativedelta(days=1)
            if "week" in datestring:
                scenedate = today - relativedelta(weeks=intervalcount)
            if "month" in datestring:
                scenedate = today - relativedelta(months=intervalcount)
            if "year" in datestring:
                scenedate = today - relativedelta(years=intervalcount)

            return scenedate.isoformat()
        return dateparser.parse('today').isoformat()
