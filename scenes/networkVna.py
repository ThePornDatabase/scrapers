import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VnaNetworkSpider(BaseSceneScraper):
    name = 'VnaNetwork'
    network = 'vna'

    start_urls = [
        'https://www.allanalallthetime.com',
        'https://kimberleelive.com',
        'https://shandafay.com',
        'https://sarajay.com',
        'https://carmenvalentina.com',
        'https://charleechaselive.com',
        'https://gabbyquinteros.com',
        'https://angelinacastrolive.com',
        'https://juliaannlive.com',
        'https://sunnylanelive.com',
        'https://pumaswedexxx.com',
        'https://sophiedeelive.com',
        'https://itscleolive.com',
        'https://maggiegreenlive.com',
        'https://tashareign.com',
        'https://jelenajensen.com',
        'https://pennypaxlive.com',
        'https://alexlegend.com',
        'https://sexmywife.com',
        'https://rubberdoll.net',
        'https://fuckedfeet.com',
        'https://ninakayy.com',
        'https://romemajor.com',
        'https://siripornstar.com',
        'https://kink305.com',
        'https://foxxedup.com',
        'https://kendrajames.com',
        'https://povmania.com',
        'https://girlgirlmania.com',
        'https://womenbyjuliaann.com',
    ]

    selector_map = {
        'title': '//h1[@class="customhcolor"]/text()',
        'description': '//*[@class="customhcolor2"]/text()',
        'date': '//*[@class="date"]/text()',
        'image': '//center//img/@src',
        'performers': '//h3[@class="customhcolor"]/text()',
        'tags': '//h4[@class="customhcolor"]/text()',
        'external_id': 'videos/(\\d+)/(.+)',
        'trailer': '',

        'pagination': '/videos/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.css('a::attr(href)').getall()
        for scene in scenes:
            if re.search(self.selector_map['external_id'], scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tagLink = self.process_xpath(
            response, self.get_selector_map('tags')).get()
        tags = []
        for tag in tagLink.strip().split(','):
            if tag.strip():
                tags.append(tag.strip().title())
        return tags

    def get_performers(self, response):
        performerLink = self.process_xpath(
            response, self.get_selector_map('performers')).get()

        performers = []
        for performer in performerLink.replace('&nbsp', '').split(','):
            if performer.strip():
                performers.append(performer.strip())

        if 'shandafay' in response.url:
            performers.append('Shanda Fay')
        if 'sexmywife' in response.url:
            performers.append('Mandy Tyler')

        return performers
