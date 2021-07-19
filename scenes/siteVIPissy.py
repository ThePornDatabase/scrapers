import re
import scrapy
import tldextract
import html

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteVIPissySpider(BaseSceneScraper):
    name = 'VIPissy'
    network = "VIPissy Cash"
    parent = "VIPissy"

    start_urls = [
        'https://www.vipissy.com',
    ]

    selector_map = {
        'title': '//section[@class="downloads"]/strong/text()',
        'description': '//div[contains(@class,"show_more")]/text()',
        'date': '//i[@class="glyphicon glyphicon-calendar"]/../following-sibling::dd[1]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[contains(@class,"row-with-video")]//video/@poster',
        'performers': '//dl/dd/a[contains(@href,"girls/")]/text()',
        'tags': '//section[@class="downloads"]//a[contains(@href,"tag")]/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '//div[contains(@class,"row-with-video")]//video/source/@src',
        'pagination': '/updates/page-%s/?&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@class="image-wrapper"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
        
    def get_site(self, response):
        return "VIPissy"


    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = self.get_from_regex(title.get(), 're_title')

            if title:
                title = html.unescape(title.strip())
                if " — " in title:
                    title = re.search(' — (.*)', title).group(1)
                return html.unescape(title.strip())
        return None

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = list(map(lambda x: x.strip(), description))
            description = " ".join(description)
            return description.strip()

        return ''
