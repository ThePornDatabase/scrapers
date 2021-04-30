import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class InterracialPassSpider(BaseSceneScraper):
    name = 'InterracialPass'
    network = 'InterracialPass'

    start_urls = [
        'https://www.interracialpass.com',
        'https://www.backroomcastingcouch.com',
        'https://blackambush.com',
        'https://exploitedcollegegirls.com',
        'https://www.ikissgirls.com'
    ]

    selector_map = {
        'title': '//h2[@class="section-title"]/text()',
        'description': '//div[@class="row"]//div[@class="update-info-block"][1]',
        'date': '//div[@class="update-info-row"]/text()',
        'image': '//div[@class="player-thumb"]//img/@src0_1x | //img[contains(@class,"main-preview")]/@src',
        'performers': '//div[contains(@class, "models-list-thumbs")]//li//span/text()',
        'tags': '//ul[@class="tags"]//li//a/text()',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            meta = {}
            if scene.xpath('//img/@src0_1x').get() is not None:
                meta['image'] = self.format_link(
                    response, scene.xpath('//img/@src0_1x').get())

            if link:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page):
        selector = '/t1/categories/movies_%s_d.html'

        if 'exploitedcollegegirls' in base:
            selector = '/site/categories/movies_%s_d.html'
        elif 'ikissgirls' in base:
            selector = '/categories/movies_%s_d.html'
        elif 'blackambush' in base:
            selector = '/categories/movies_%s_d.html'
        elif 'backroomcastingcouch' in base:
            selector = '/site/categories/movies_%s_d.html'

        return self.format_url(base, selector % page)

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).extract()
        return dateparser.parse(date[1].strip()).isoformat()
