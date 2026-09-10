import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAnalJesseSpider(BaseSceneScraper):
    name = 'AnalJesse'
    network = 'Anal Jesse'
    parent = 'Anal Jesse'
    site = 'Anal Jesse'

    start_urls = [
        'https://analjesse.com',
    ]

    selector_map = {
        'description': '//div[contains(@class, "vidImgContent")]/p//text()',
        'performers': '',
        'tags': '',
        'external_id': r'/scenes/(.*?)_vids\.html',
        'trailer': '',
        'pagination': '/categories/movies%s.html',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        # Page one is /categories/movies.html; later pages are movies_2.html, movies_3.html ...
        suffix = '' if int(page) == 1 else '_%d' % int(page)
        return self.format_url(self.start_urls[0], self.get_selector_map('pagination') % suffix)

    def get_scenes(self, response):
        # The listing carries title, date, duration, thumbnail and the set id, so those
        # are passed through and only the description is read off the scene page.
        for scene in response.xpath('//div[contains(@class, "latestUpdateB")][@data-setid]'):
            link = scene.xpath('.//h4//a/@href').get()
            if not link:
                continue

            meta = {}
            meta['id'] = scene.xpath('./@data-setid').get()

            title = scene.xpath('.//h4//a/text()').get()
            if title:
                meta['title'] = self.cleanup_title(title)

            info = [self.cleanup_text(x) for x in scene.xpath('.//ul[@class="videoInfo"]/li//text()').getall()]
            info = [x for x in info if x]

            scenedate = next((x for x in info if re.search(r'\d{4}', x)), None)
            if scenedate:
                scenedate = self.parse_date(scenedate, date_formats=['%b %d, %Y', '%B %d, %Y'])
                if scenedate:
                    meta['date'] = scenedate.strftime('%Y-%m-%d')

            duration = next((x for x in info if re.search(r'\d+\s*min', x)), None)
            if duration:
                meta['duration'] = str(int(re.search(r'(\d+)', duration).group(1)) * 60)

            # poster_4x is the largest still; the src on the <video> is a preview clip
            image = scene.xpath('.//video/@poster_4x | .//video/@poster_3x | .//video/@poster_2x').get()
            if image:
                meta['image'] = self.format_link(response, image.replace('//content', '/content'))

            trailer = scene.xpath('.//video/@src | .//video/source/@src').get()
            if trailer:
                meta['trailer'] = self.format_link(response, trailer.replace('//content', '/content'))

            meta['performers'] = []
            meta['performers'].append('Jesse Thai')

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)
