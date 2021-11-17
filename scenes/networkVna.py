import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VnaNetworkSpider(BaseSceneScraper):
    name = 'VnaNetwork'
    network = 'vna'

    start_urls = [
        'https://alexlegend.com',
        'https://www.allanalallthetime.com',
        'https://angelinacastrolive.com',
        'https://carmenvalentina.com',
        'https://charleechaselive.com',
        'https://foxxedup.com',
        'https://fuckedfeet.com',
        'https://gabbyquinteros.com',
        'https://girlgirlmania.com',
        'https://itscleolive.com',
        'https://jelenajensen.com',
        'https://juliaannlive.com',
        'https://kaylapaigelive.com',
        'https://kendrajames.com',
        'https://kimberleelive.com',
        'https://kink305.com',
        'https://maggiegreenlive.com',
        'https://maxinex.com',
        'https://ninakayy.com',
        'https://pennypaxlive.com',
        'https://povmania.com',
        'https://pumaswedexxx.com',
        'https://romemajor.com',
        'https://rubberdoll.net',
        'https://sarajay.com',
        'https://sexmywife.com',
        'https://shandafay.com',
        'https://siripornstar.com',
        'https://sophiedeelive.com',
        'https://sunnylanelive.com',
        'https://tashareign.com',
        'https://vickyathome.com',
        'https://womenbyjuliaann.com',

        # Invalid VNA Sites, here for reference
        # Can't be scraped for various reasons...  Locked, no pagination, no video page, etc
        # ~ https://bobbiedenlive.com
        # ~ https://deauxmalive.com
        # ~ https://nataliastarr.com
        # ~ https://nikkibenz.com
        # ~ https://rachelstormsxxx.com
        # ~ https://samanthagrace.com

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
        taglink = self.process_xpath(
            response, self.get_selector_map('tags')).get()
        tags = []
        for tag in taglink.strip().split(','):
            if tag.strip():
                tags.append(tag.strip().title())
        return tags

    def get_performers(self, response):
        performerlink = self.process_xpath(
            response, self.get_selector_map('performers')).get()

        performers = []
        for performer in performerlink.replace('&nbsp', '').split(','):
            if performer.strip():
                performers.append(performer.strip())

        if 'shandafay' in response.url:
            performers.append('Shanda Fay')
        if 'sexmywife' in response.url:
            performers.append('Mandy Tyler')

        return performers

    def get_next_page_url(self, base, page):
        if "vickyathome" in base:
            return self.format_url(base, "/milf-videos/page/%s" % page)
        return self.format_url(base, self.get_selector_map('pagination') % page)
