import re
import string
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBiLatinMenSpider(BaseSceneScraper):
    name = 'BiLatinMen'
    network = 'Bi Latin Men'
    parent = 'Bi Latin Men'
    site = 'Bi Latin Men'

    start_urls = [
        'http://bilatinmen.com',
    ]

    selector_map = {
        'title': '//h2[@class="modelName"]/text()|//td[@class="title" and @colspan="3"]/text()[1]',
        'description': '//div[@class="col-md-12"]/p/text()|//td[@class="eroticstorytext"]/p//text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '//h2[@class="modelName"]/text()|//td[@class="title" and @colspan="3"]/text()[1]',
        'tags': '',
        'duration': '',
        'trailer': '//video/source[contains(@type, "mp4")]/@src',
        'external_id': r'.*_(\d+)\.',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "http://bilatinmen.com/index1.html"
        elif int(page) == 2:
            return "http://bilatinmen.com/nudelatinmen.html"
        else:
            page = str(int(page) - 1)
            pagination = "/latin_men_preview/previews_latin_men_0%s.htm"
            return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        page = int(meta['page'])
        if page == 1:
            scenes = response.xpath('//div[contains(@class, "update-item") and not(contains(.//a/@href, "erotic_stories")) and not(contains(.//a/@href, "erotic_art")) and not(contains(.//h3/a/text(), "Pics:")) and not(contains(.//h2/text(), "Free Stuff"))]')
        elif page == 2:
            scenes = response.xpath('//div[contains(@class, "update-item")]//h3/a/@href').getall()
        else:
            scenes = response.xpath('//a[contains(@href, "latin_men_preview")]/@href').getall()
        for scene in scenes:
            if page == 1:
                scenedate = scene.xpath('.//p/text()')
                if scenedate:
                    scenedate = scenedate.get()
                    scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate)
                    if scenedate:
                        scenedate = scenedate.group(1)
                        meta['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')
                scene = scene.xpath('./div[1]/div[1]//a/@href').get()
            if page == 2:
                scene = "latin_men_preview/" + scene
            if re.search(self.get_selector_map('external_id'), scene) and "previews_latin_men" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performer_string = response.xpath('//h2[@class="modelName"]/text()|//td[@class="title" and @colspan="3"]/text()[1]')
        performers = []
        if performer_string:
            performer_string = html.unescape(performer_string.get())
            performer_string = performer_string.replace(",", "&")
            performers = performer_string.split("&")
            performers = list(map(lambda x: string.capwords(x.strip()), performers))
        return performers
