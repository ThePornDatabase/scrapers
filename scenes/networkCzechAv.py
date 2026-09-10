import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class CzechAvSpider(BaseSceneScraper):
    name = 'CzechAv'
    network = 'Czech Casting'

    start_urls = [
        'https://czechamateurs.com',
        'https://czechbangbus.com',
        'https://czechbitch.com',
        'https://czechcabins.com',
        'https://czechcouples.com',
        'https://czechdungeon.com',
        'https://czechestrogenolit.com',
        'https://czechexperiment.com',
        'https://czechfantasy.com',
        'https://czechfirstvideo.com',
        'https://czechgame.com',
        'https://czechgangbang.com',
        'https://czechgardenparty.com',
        'https://czechharem.com',
        'https://czechhomeorgy.com',
        'https://czechlesbians.com',
        'https://czechmassage.com',
        'https://czechmegaswingers.com',
        'https://czechorgasm.com',
        'https://czechparties.com',
        'https://czechpawnshop.com',
        'https://czechpool.com',
        'https://czechsauna.com',
        'https://czechsharking.com',
        'https://czechsnooper.com',
        'https://czechsolarium.com',
        'https://czechspy.com',
        'https://czechstreets.com',
        'https://czechsupermodels.com',
        'https://czechtantra.com',
        'https://czechtaxi.com',
        'https://czechtoilets.com',
        'https://czechtwins.com',
        'https://czechwifeswap.com',
    ]

    selector_map = {
        # h2.nice-title is gone; the full title (with the episode prefix) is in og:title
        'title': "//meta[@property='og:title']/@content",
        'date': '//script[contains(@type, "json")]/text()',
        're_date': r'uploadDate[\'\"].*?(\d{4}-\d{2}-\d{2})',
        'description': '//script[contains(@type, "json")]/text()',
        're_description': r'description[\'\"].*?[\'\"](.*?)[\'\"]',
        'image': "//meta[@property='og:image']/@content",
        'tags': "",
        'external_id': r'/video/(.+?)/',
        'trailer': '//script[contains(@type, "json")]/text()',
        're_trailer': r'contentUrl[\'\"]\s*:\s*[\'\"](https?://[^\'\"]+)',
        # /tour/videos/page-N/ 404s; each site now serves its whole listing on the
        # root.  The /page-N/ variants answer 404 and just reshuffle the same set,
        # so there is no pagination left to walk.
        'pagination': ''
    }

    async def start(self):
        # The base builds page one out of 'pagination', which is empty here
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.parse, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        # div.episode-list is gone; the cards link straight to /video/<slug>/
        scenes = response.xpath('//a[contains(@href, "/video/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = response.xpath('//script[contains(@type, "json")]/text()')
        if tags:
            tags = re.search(r'keywords[\'\"].*?[\'\"](.*?)[\'\"]', tags.get())
            if tags:
                tags = tags.group(1)
                tags = tags.split(",")
                tags = list(map(lambda x: string.capwords(x.strip()), tags))
        return tags
