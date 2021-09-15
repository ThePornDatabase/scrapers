import re
import string
import dateparser
import html
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCruelGirlfriendSpider(BaseSceneScraper):
    name = 'CruelGirlfriend'
    network = 'Cruel Girlfriend'

    start_urls = [
        'https://cruelgf.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//main/div[@class="row"][2]/div/div/h3/text()',
        'date': '',
        'image': '//div[@class="info-box-white2"]/video/@poster',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//main/div[@class="row"][3]/div/div/h3/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/CGUpdates%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"col-md-third")]')
        for scene in scenes:
            title = scene.xpath('./div[contains(@class, "Title")]/text()')
            if title:
                title = string.capwords(title.get().strip())
            else:
                title = False

            performers = scene.xpath('.//div[contains(@class, "Name")]/a/text()')
            if performers:
                performers = list(map(lambda x: string.capwords(x.strip()), performers.getall()))
                if '' in performers:
                    performers.remove('')
            else:
                performers = False

            date = scene.xpath('./div[contains(@class, "Date")]/text()')
            if date:
                date = dateparser.parse(date.get(), date_formats=['%d %b %Y']).isoformat()
            else:
                date = dateparser.parse('today').isoformat()

            scene = scene.xpath('./div[contains(@class,"LatestUpdate-Pink")]/div/a/@href').get()
            scene = self.format_link(response, scene)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene),
                                    callback=self.parse_scene,
                                    meta={'title': title, 'date': date, 'performers': performers}
                                    )

    def get_site(self, response):
        return "Cruel Girlfriend"

    def get_parent(self, response):
        return "Cruel Girlfriend"

    def get_id(self, response):
        externid = super().get_id(response)
        externid = externid.replace("%20", "")
        externid = re.sub('[^a-zA-Z0-9-]', '', externid)
        return externid.lower().strip()

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = list(map(lambda x: x.strip(), description.getall()))
            description = " ".join(description)
            return html.unescape(description.strip())
        return ''

    def get_tags(self, response):
        tags = super().get_tags(response)
        if '' in tags:
            tags.remove('')
        return tags
