import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NubilesSpider(BaseSceneScraper):
    name = 'Nubiles'
    network = 'nubiles'

    start_urls = [
        "https://anilos.com/video/gallery",
        "https://badteenspunished.com/video/gallery",
        "https://bountyhunterporn.com/video/gallery",
        "https://brattysis.com/video/gallery",
        "https://daddyslilangel.com/video/gallery",
        "https://deeplush.com/video/gallery",
        "https://detentiaongirls.com/video/gallery",
        "https://driverxxx.com/video/gallery",
        "https://familyswap.xxx/video/gallery",
        "https://momsteachsex.com/video/gallery",
        "https://myfamilypies.com/video/gallery",
        "https://nfbusty.com/video/gallery",
        "https://nubilefilms.com/video/gallery",
        "https://nubiles-casting.com/video/gallery",
        "https://nubiles-porn.com/video/gallery",
        "https://nubiles.net/video/gallery",
        "https://nubileset.com/video/gallery",
        "https://nubilesunscripted.com/video/gallery",
        "https://petitdehdporn.com/video/gallery",
        "https://petiteballerinasfucked.com/video/gallery",
        "https://princesscum.com/video/gallery",
        "https://stepsiblingscaught.com/video/gallery",
        "https://teacherfucksteens.com/video/gallery",
        "https://thatsitcomshow.com/video/gallery",
    ]

    selector_map = {
        'title': '//*[contains(@class, "content-pane-title")]/h2/text()',
        'description': '.row .collapse::text',
        'date': '//span[@class="date"]/text()',
        'image': '//video/@poster | //img[@class="fake-video-player-cover"]/@src',
        'performers': '//a[@class="content-pane-performer model"]/text()',
        'tags': '//*[@class="categories"]//a/text()',
        'external_id': '(\\d+)',
        'trailer': '',
        'pagination': '/video/gallery/%s'
    }

    def get_scenes(self, response):
        scenes = response.css(".content-grid-item>figure")
        for scene in scenes:
            link = scene.css('.img-wrapper > a::attr(href)').extract_first()
            if re.search('video\\/watch', link) is not None:
                meta = {
                    'title': scene.css('.title a::text').get().strip(),
                    'date': dateparser.parse(scene.css('.date::text').extract_first()).isoformat()
                }

                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath(
            '//meta[@property="og:site_name"]/@content').get().replace("'", "")
        if site:
            return site

        return super().get_site(response)

    def get_next_page_url(self, base, page):
        page = (page - 1) * 10
        return self.format_url(
            base, self.get_selector_map('pagination') % page)
