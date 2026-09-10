import html
import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXConfessionsSpider(BaseSceneScraper):
    name = 'XConfessions'
    network = 'XConfessions'
    parent = 'XConfessions'

    start_urls = [
        'https://xconfessions.com',
    ]

    # The tour was rebuilt: the data-cy="hover-wrapper" cards are gone, the
    # performer links moved from data-cy="performer-link" to /performers/ hrefs,
    # and the per-film JSON-LD is now a @graph whose Movie node carries the date,
    # poster and director.  The "Scene markers" strip is act labels only -- no
    # timestamps are rendered -- so those are folded into the tags.
    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "description-block")]//text()',
        'performers': '//a[contains(@href, "/performers/")]/text()',
        'tags': '//a[contains(@href, "/categories/")]/text()',
        'duration': '//span[contains(@class, "uppercase") and contains(text(), " min")]/text()',
        're_duration': r'(\d+)\s*min',
        'director': '//a[contains(@href, "/collaborators/directors/")]/text()',
        'external_id': r'.*\/(.*)',
        'trailer': '',
        'pagination': '/film?order=default&page=%s',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://xconfessions.com/film?order=default"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//a[contains(@href, "/film/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_movie_node(self, response):
        if 'movienode' not in response.meta:
            node = {}
            for blob in response.xpath('//script[@type="application/ld+json"]/text()').getall():
                try:
                    data = json.loads(blob)
                except ValueError:
                    continue
                for entry in data.get('@graph', []) if isinstance(data, dict) else []:
                    if isinstance(entry, dict) and entry.get('@type') == 'Movie':
                        node = entry
                        break
                if node:
                    break
            response.meta['movienode'] = node
        return response.meta['movienode']

    def get_site(self, response):
        return "XConfessions"

    def get_date(self, response):
        created = self.get_movie_node(response).get('dateCreated')
        if created:
            return self.parse_date(created.split(" ")[0], date_formats=['%Y-%m-%d']).isoformat()
        return None

    def get_image(self, response):
        image = self.get_movie_node(response).get('image')
        if image:
            return image
        return ''

    def get_description(self, response):
        desc_rows = self.process_xpath(response, self.get_selector_map('description')).getall()
        if desc_rows:
            description = ' '.join(desc.strip() for desc in desc_rows if desc.strip())
            return self.cleanup_description(html.unescape(description.strip()))
        return ''

    def get_tags(self, response):
        tags = super().get_tags(response)
        # The "Scene markers" strip labels the acts in the film but renders no
        # timestamps, so they are only useful as tags.
        markers = response.xpath('//h2[contains(text(), "Scene markers")]/following-sibling::nav[1]//button/text()').getall()
        for marker in markers:
            marker = self.cleanup_text(marker)
            if marker and marker not in tags:
                tags.append(marker)
        return tags

    def get_director(self, response):
        director = response.xpath(self.get_selector_map('director'))
        if director:
            return self.cleanup_title(director.get().replace("\n", " ").replace("  ", " "))
        return self.get_movie_node(response).get('director') or ''

    def get_duration(self, response):
        duration = super().get_duration(response)
        if duration:
            duration = str(int(duration) * 60)
        return duration
