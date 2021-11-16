import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class FTVGirlsScraper(BaseSceneScraper):
    name = 'FTVGirls'
    network = 'RHS Photography'
    parent = 'RHS Photography'

    start_urls = [
        'https://www.ftvgirls.com/',
        'https://www.ftvmilfs.com/',
    ]

    selector_map = {
        'title': '//h1[@class="videotitle"]/text()',
        'description': '//div[@id="Bio"]//p/text()',
        'date': "",
        'image': '//img[@id="Magazine"]/@src',
        'performers': '//div[@id="BioHeader"]/h1/text()',
        'tags': "",
        'external_id': r'update\/(.*).html',
        'trailer': '//a[@class="jackbox"]/@href',
        'pagination': '/updates-%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="ModelContainer"]')
        for scene in scenes:
            taglist = []

            title = scene.xpath('.//div[@class="ModelName"]/h2/text()')
            if title:
                title = self.cleanup_title(title.get())
            else:
                title = ''

            date = scene.xpath('.//div[@class="UpdateDate"]/h3/text()')
            if date:
                date = self.parse_date(date.get().strip()).isoformat()
            else:
                date = self.parse_date('today').isoformat()

            tags = scene.xpath('.//div[contains(@class,"Tags")]/img/@title').getall()
            if tags:
                for tag in tags:
                    if " - " in tag:
                        tag = re.search('(.*) - ', tag).group(1)
                        if tag:
                            taglist.append(tag)
            else:
                tags = []

            sceneurl = scene.xpath('.//div[@class="ModelPhoto"]/a/@href').get()
            if sceneurl:
                if re.search(self.get_selector_map('external_id'), sceneurl):
                    yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta={'date': date, 'tags': taglist, 'title': title})

    def get_performers(self, response):
        performerlist = []
        measurements = response.xpath('//h2/b[contains(text(), "Figure")]/following-sibling::text()').getall()
        performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
        x = 0
        for performer in performers:
            name_measurements = re.sub(r'\W+', '', measurements[x].strip())
            performer = performer.replace("'s Statistics", "").strip() + "  " + name_measurements
            x = x + 1
            performerlist.append(performer)

        if performerlist:
            return performerlist
        return []

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        externid = search.group(1)
        externid = externid.zfill(4)
        return externid
