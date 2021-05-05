import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class ErosArtsSpider(BaseSceneScraper):
    name = 'ErosArts'
    network = "Eros Arts"

    start_urls = [
        'https://www.jerkoffinstructions.com/',
        'https://www.sexpov.com/',
        'https://www.stepmomfun.com/',
        'https://www.taboohandjobs.com/',
        'https://www.taboopov.com/'
    ]

    selector_map = {
        'title': '//div[@class="title"]/text()',
        'description': '//div[@class="title"]/following::p/text()',
        'date': "//div[@class='views']/span/text()",
        'image': '//img[@class="photo"]/@src',
        'performers': '//a[contains(@href,"/models/")]/text()',
        'tags': "//a[contains(@href,'/keywords/')]/text()",
        'external_id': '\/videos\/(.*)\/',
        'trailer': '',
        'pagination': '/tour.php?p=%s#'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//td[@valign='top'][@width='300']/a[contains(@href,'/videos/')]/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        search = re.search('Date Added: (\d{1,2}\/\d{1,2}\/\d{4})', response.text)
        scenedate = dateparser.parse(search.group(1)).isoformat()
        return scenedate

    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title')).get().strip()
        if "|" in title:
            title = title.replace(u'\xa0', u' ')
            title = title.replace("|", "").strip()

        return title
