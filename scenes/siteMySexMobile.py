import json
import string
import html
import datetime
from dateutil.relativedelta import relativedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMySexMobileSpider(BaseSceneScraper):
    name = 'MySexMobile'
    network = 'My Sex Mobile'

    start_urls = [
        'https://mysexmobile.com',
    ]

    selector_map = {
        'title': '',
        'description': '//div[@class="row"]/div[contains(@class,"scene-desc")]/p//text()',
        'date': '',
        'image': '',
        'performers': '//div[@class="row"]/p/a[contains(@href,"/girls")]/text()',
        'tags': '//div[@class="row"]/p/a[not(contains(@href,"/girls"))]/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/ajax/main/%s?locale_lang=en&sort=newest&take=10'
    }

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['scenes']
        for scene in jsondata:
            sceneid = scene
            scenedate = jsondata[scene]['days_ago']
            if scenedate:
                today = datetime.datetime.now()
                scenedate = today - relativedelta(days=scenedate)
                scenedate = scenedate.isoformat()
            sceneimage = jsondata[scene]['thumbnail']['filepath']
            scenetitle = string.capwords(jsondata[scene]['title'])
            sceneurl = jsondata[scene]['url']
            if sceneid:
                yield scrapy.Request(sceneurl, callback=self.parse_scene, meta={'date': scenedate, 'id': sceneid, 'title': scenetitle, 'image': sceneimage})

    def get_site(self, response):
        return "My Sex Mobile"

    def get_parent(self, response):
        return "My Sex Mobile"

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = " ".join(description.getall())
            description = description.replace("\n", "").replace("\r", "").replace("\t", "").replace("  ", " ")
            return html.unescape(description.strip())

        return ''
