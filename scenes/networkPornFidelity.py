import re

import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.http import HtmlResponse


class PornFidelitySpider(BaseSceneScraper):
    name = 'PornFidelity'
    network = 'pornfidelity'

    start_urls = [
        # 'https://www.teenfidelity.com',
        'https://www.pornfidelity.com',
        # 'https://www.kellymadison.com'
    ]
    cookies = {'nats': 'MC4wLjMuNTguMC4wLjAuMC4w'}

    selector_map = {
        'title': '//div[@class="level-item"]/text()',
        'description': '//div[@class="column is-three-fifths"]/text()',
        'date': "",
        'image': '',
        'performers': '//a[@class="is-underlined"]/text()',
        'tags': "",
        'duration': '//li//text()[contains(., "mins")]',
        're_duration': r'(\d{1,2}\:\d{2}) mins',
        'external_id': 'episodes\\/(\\d+)',
        'trailer': '',
        'pagination': "/episodes/search?page=%s"
    }

    def get_scenes(self, response):
        rsp = HtmlResponse(url=response.url, body=response.json()[
                           'html'], encoding='utf-8')
        scenes = rsp.css('.episode .card-link::attr(href)').extract()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, cookies=self.cookies)

    def get_image(self, response):
        res = re.search(self.get_selector_map('external_id'), response.url)
        return 'https://tour-cdn.kellymadisonmedia.com/content/episode/poster_image/%s/poster.jpg' % res.group(
            1)

    def get_date(self, response):
        search = re.search('Published: (\\d+-\\d+-\\d+)', response.text)
        if search:
            return dateparser.parse(search.group(1)).strftime('%Y-%m-%d')
        else:
            return None

    def get_title_full(self, response):
        return response.xpath(self.get_selector_map('title'))[1].get().strip()

    def get_title(self, response):
        print(response)
        title = self.get_title_full(response)
        search = re.search('(.+) - .+ \\#(\\d+)', title)
        if not search:
            return title
        return search.group(1).strip() + ' E' + search.group(2).strip()

    def get_site(self, response):
        title = response.xpath(self.get_selector_map('title'))[1].get().strip()
        search = re.search('.+ - (.+) #(\\d+)', title)
        if search:
            return search.group(1).strip()

        if 'Teenfidelity' in title:
            return 'TeenFidelity'
        elif 'Kelly Madison' in title:
            return 'Kelly Madison'
        else:
            return 'PornFidelity'

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("Episode Summary", "").strip()
        return description
