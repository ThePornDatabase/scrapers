import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBreederFuckersSpider(BaseSceneScraper):
    name = 'BreederFuckers'
    network = 'Straight Hell Videos'
    parent = 'Straight Hell Videos'
    site = 'Breeder Fuckers'

    start_urls = [
        'https://straighthellvideos.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/tag/breederfuckers-com/page/%s/',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h2/a/text()').get()
            item['title'] = self.cleanup_title(title.replace("#", ""))

            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::span/text()')
            if scenedate:
                scenedate = scenedate.get()
                item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')

            image = scene.xpath('.//div[contains(@class, "featured")]/img/@src')
            if image:
                image = image.get()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)

            description = scene.xpath('.//div[contains(@class, "full-post")]/p/text()')
            if description:
                description = description.getall()
                description[:] = [s.replace("\r", "").replace("\n", "").replace("\t", "").strip() for s in description]
                item['description'] = " ".join(description)

            item['tags'] = scene.xpath('.//i[contains(@class, "fa-tags")]/following-sibling::a[contains(@href, "/fetishes/") or contains(@href, "training")]/text()').getall()

            item['network'] = 'Straight Hell Videos'
            item['parent'] = 'Straight Hell Videos'
            item['site'] = 'BreederFuckers'
            item['type'] = "Scene"

            performers = scene.xpath('.//i[contains(@class, "fa-tags")]/following-sibling::a[(contains(@href, "/straight-slaves/") or contains(@href, "/masters/")) and not(contains(@href, "fetish"))]/text()')
            if performers:
                performers = performers.getall()
                item['performers'] = []
                item['performers_data'] = []
                for performer in performers:
                    performer_extra = {}
                    performer_extra['name'] = performer
                    performer_extra['site'] = "Straight Hell Videos"
                    performer_extra['extra'] = {}
                    performer_extra['extra']['gender'] = "Male"
                    item['performers_data'].append(performer_extra)
                    item['performers'].append(performer)

            item['url'] = scene.xpath('./a[1]/@href').get()
            item['id'] = re.search(r'.*/(.*?)/', item['url']).group(1)

            trailer = scene.xpath('.//div[contains(@data-item, "mp4")]/@data-item')
            if trailer:
                trailer = trailer.get()
                trailer = trailer.replace("\\/", "/")
                trailer = re.search(r'.*?(http.*?)[\'\"]', trailer)
                if trailer:
                    item['trailer'] = trailer.group(1)

            yield self.check_item(item, self.days)
