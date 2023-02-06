import scrapy

from extruct.jsonld import JsonLdExtractor
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class VRLifeSpider(BaseSceneScraper):
    name = 'VRLife'
    network = 'VRLife'
    parent = 'VRLife'
    start_urls = [
        'https://virtualrealporn.com',
        'https://virtualrealtrans.com',
        'https://virtualrealpassion.com',
        'https://virtualrealgay.com',
        'https://virtualrealjapan.com',
        'https://virtualrealamateurporn.com',
    ]

    selector_map = {
        'id': './@data-id',
        'url': './/a[contains(@class, "w-portfolio-item-anchor")]/@href',
        'title': './/img/@alt',
        'tags': '//div[@class="metaSingleData"]//a/span/text()',
        'external_id': r'-(\d+)/?$',
        'pagination': '/?videoPage=%s'        
    }

    def get_scenes(self, response):
        scenes = response.xpath("//div[@data-id and contains(@class, 'videoItem')]")
        
        for scene in scenes:
            scene_id = self.process_xpath(scene, self.get_selector_map('id')).get()
            title = self.process_xpath(scene, self.get_selector_map('title')).get()
            url = self.process_xpath(scene, self.get_selector_map('url')).get()
            yield scrapy.Request(url=self.format_link(response, url), callback=self.parse_scene, meta={'id': scene_id, 'title': title})

    def parse_scene(self, response):
        jslde = JsonLdExtractor()
        json = jslde.extract(response.text)
        data = {}
        for obj in json:
            if '@type' in obj and obj['@type'] == 'Movie':
                data = obj
                break

        item = SceneItem()
        item['title'] = self.clean_title(response.meta['title'])
        item['description'] = self.cleanup_description(data['description'])
        item['image'] = data['image']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])        
        item['id'] = response.meta['id']
        item['trailer'] = self.format_link(response, data['trailer']['contentUrl'])
        item['duration'] = self.duration_to_seconds(data['duration'])
        item['url'] = response.url
        item['date'] = self.parse_date(data['datePublished']).isoformat()
        item['network'] = self.network
        item['site'] = self.get_site(response)
        item['parent'] = self.parent

        item['performers'] = []
        for model in data['actors']:
            item['performers'].append(model['name'])

        item['tags'] = self.get_tags(response)        
        yield item

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "VR" not in tags:
            tags.append("VR")
        return tags
    
    @staticmethod
    def clean_title(title):
        # virtualrealjapan.com uses funky brackets, cleaning up for astethics
        return title.replace("【", "[").replace("】", "] ")
