import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlackBullChallengeSpider(BaseSceneScraper):
    name = 'BlackBullChallenge'
    network = 'Black Bull Challenge'
    parent = 'Black Bull Challenge'
    site = 'Black Bull Challenge'

    start_urls = [
        'https://blackbullchallenge.com',
    ]

    selector_map = {
        'description': '//div[contains(@class, "vidImgContent")]/p//text()',
        'tags': '//a[contains(@href, "/categories/")]/text()',
        'external_id': r'/scenes/(.*?)_vids\.html',
        'trailer': '',
        'pagination': '/categories/movies%s.html',
        'type': 'Scene',
    }

    # "Videos" is the section link that sits alongside the real category tags
    tag_trash = ['videos']

    def get_next_page_url(self, base, page):
        # Page one is /categories/movies.html; later pages are movies_2.html, movies_3.html ...
        suffix = '' if int(page) == 1 else '_%d' % int(page)
        return self.format_url(self.start_urls[0], self.get_selector_map('pagination') % suffix)

    def get_scenes(self, response):
        # The listing carries title, performers, duration, thumbnail and the set id, so
        # only the description and tags are read off the scene page.
        for scene in response.xpath('//div[contains(@class, "latestUpdateB")][@data-setid]'):
            link = scene.xpath('.//h4//a/@href').get()
            if not link:
                continue

            meta = {}
            meta['id'] = scene.xpath('./@data-setid').get()

            title = scene.xpath('.//h4//a/text()').get()
            if title:
                meta['title'] = self.cleanup_title(title)

            performers = scene.xpath('.//a[contains(@href, "/models/")]/text()').getall()
            meta['performers'] = [self.cleanup_text(x) for x in performers if x.strip()]

            duration = scene.xpath('.//ul[@class="videoInfo"]/li//text()').re_first(r'(\d+)\s*min')
            if duration:
                meta['duration'] = str(int(duration) * 60)

            # Released scenes read "Available to Members Now!" and carry no date; only
            # upcoming ones show one, which check_item then filters out as future-dated.
            avail = ' '.join(scene.xpath('.//div[contains(@class, "avail_date")]//text()').getall())
            scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', avail)
            if scenedate:
                scenedate = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y'])
                if scenedate:
                    meta['date'] = scenedate.strftime('%Y-%m-%d')

            # poster_4x is the largest still; the <video> src is a preview clip
            image = scene.xpath('.//video/@poster_4x | .//video/@poster_3x | .//video/@poster_2x').get()
            if image:
                meta['image'] = self.format_link(response, image.replace('//content', '/content'))

            trailer = scene.xpath('.//video/@src | .//video/source/@src').get()
            if trailer:
                meta['trailer'] = self.format_link(response, trailer.replace('//content', '/content'))

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        return [tag for tag in tags if tag.lower() not in self.tag_trash]
