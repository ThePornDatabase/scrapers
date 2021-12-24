import re
from datetime import datetime

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class TugPassSpider(BaseSceneScraper):
    name = 'TugPass'
    network = "TugPass"

    start_urls = [
        'https://www.tugpass.com',

        #  Network sub-sites for reference
        # 'https://www.clubtug.com',
        # 'https://www.cumblastcity.com',
        # 'https://www.ebonytugs.com',
        # 'https://www.edgequeens.com',
        # 'https://www.finishhim.com',
        # 'https://www.meanmassage.com',
        # 'https://www.mylked.com',
        # 'https://www.over40handjobs.com',
        # 'https://www.petite18.com',
        # 'https://www.seemomsuck.com',
        # 'https://www.shadyspa.com',
        # 'https://www.teasepov.com',
        # 'https://www.teentugs.com'
    ]

    selector_map = {
        'title': '//h3[contains(@class,"box-title")]/text()',
        'description': '//div[contains(@class,"video-content")]/p/strong/following-sibling::text()',
        'date': "//div[@class='views']/span/text()",
        'image': '//div[@class="player"]/img/@src',
        'performers': 'Performers not borken out on sit',
        'tags': "",
        'external_id': '\\/videos\\/(.*).htm',
        'trailer': '',
        'pagination': '/updates_%s.html'
    }

    # This is one of those sites with Date and Site on the index, so have to
    # pull it from the outer loop
    def get_scenes(self, response):
        parentxpath = response.xpath("//div[@class='item-wrap']")

        for child in parentxpath:
            testvalid = child.xpath(".//div[@class='item-content']")
            if len(testvalid) > 0:
                date = child.xpath(".//span[@class='date']/text()").get()
                try:
                    site = child.xpath(
                        ".//a[@class='tag-btn']/text()").get().strip()
                except BaseException:
                    site = "TugPass"

                if date:
                    date = self.parse_date(date).isoformat()
                else:
                    date = self.parse_date('today').isoformat()

                if ".com" in site:
                    site = re.search('(.*?)\\.com', site).group(1).strip()

                scene = child.xpath(".//h4/a/@href").get()
                if "?nats" in scene:
                    scene = re.search("(.*)(\\?nats)", scene).group(1).strip()

                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                         meta={'date': date, 'site': site})

    def get_date(self, response):
        return datetime.now().isoformat()

    def get_image(self, response):
        html_response = response.text
        if "posterImage:" in html_response:
            image = re.search(
                'posterImage:\\ \'(.*?)\',',
                html_response).group(1)
        else:
            image = self.process_xpath(
                response, self.get_selector_map('image')).get()
        return self.format_link(response, image)
