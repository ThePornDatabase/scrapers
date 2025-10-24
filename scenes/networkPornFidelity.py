import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


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
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[contains(text(), "Episode Summary")]/following-sibling::p[1]/text()',
        'date': '//p[contains(text(), "Published:")]//text()[contains(., "-")]',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//p[contains(text(), "Starring:")]/a/text()',
        'tags': "",
        'duration': '//p[contains(text(), "Episode:")]//text()[contains(., "mins")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'external_id': 'episodes\\/(\\d+)',
        'trailer': '',
        'pagination': "/episodes/search?page=%s"
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class, "video-card")]/ancestor::div[1]')
        for scene in scenes:
            episode = scene.xpath('.//span[contains(@class, "video-title")]/text()')
            if episode:
                episode = episode.get()
                episode = re.sub(r'[^0-9]+', '', episode)
                meta['episode'] = episode
            title = scene.xpath('.//h3[contains(@class, "video-title")]/text()')
            if title:
                title = title.get()
                title = self.cleanup_title(title.strip())
                if episode:
                    title = f"{title} E{episode}"
                meta['title'] = title

            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::span[1]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = self.parse_date(scenedate, date_formats=['%m/%d/%y']).strftime('%Y-%m-%d')
                if scenedate:
                    meta['date'] = scenedate

            site = scene.xpath('.//span[contains(@class, "badge-brand")]/text()')
            if site:
                site = site.get()
                site = site.lower().strip()
                if site == "tf":
                    meta['site'] = "TeenFidelity"
                    meta['parent'] = "PornFidelity"
                if site == "pf":
                    meta['site'] = "PornFidelity"
                if site == "km":
                    meta['site'] = "KellyMadison"
                    meta['parent'] = "PornFidelity"
                if not site:
                    meta['site'] = "PornFidelity"

            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        meta = response.meta
        title = super().get_title(response)
        if "episode" in meta and meta['episode']:
            return f"{title} E{meta['episode']}"
        else:
            return title

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("Episode Summary", "").strip()
        return description

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.xpath('//main/div[contains(@class,"maintop-first-section")]//img[contains(@class,"object-fit-cover")]/@src')
            if image:
                image = self.format_link(response, image.get())

        if not image:
            image = ""
        return image
