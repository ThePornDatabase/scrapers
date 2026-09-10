import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class FamilyTherapyXXXSpider(BaseSceneScraper):
    name = 'FamilyTherapyXXX'

    start_urls = [
        'https://familytherapyxxx.com',
        'https://teenlovesblack.com',
        'https://wifelovesblack.com',
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': '//div[@class="entry-content"]/p[1]/text()',
        'performers': '//div[@class="entry-content"]/p[contains(text(),"Starring")]/text()',
        'date': '//span[@class="published"]/text()',
        # ~ 'image': '',
        'tags': '//p[@class="post-meta"]/a[contains(@rel,"category")]/text()',
        'external_id': r'\.com\/(.*)\/',
        'trailer': '//meta[@itemprop="contentUrl"]/@content',
        'pagination': '/page/%s'
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class,"salvattore_content")]//article[contains(@id,"post")]')
        for scene in scenes:
            image = scene.xpath('./div/a/img/@src')
            if image:
                image = self.format_link(response, image.get())
            else:
                image = ''
            meta['image'] = image
            scene = scene.xpath('./div/a/@href').get()

            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_performers(self, response):
        if "teenlovesblack" in response.url or "wifelovesblack" in response.url:
            performers = response.xpath('//text()[contains(., "Tags:")]/following-sibling::a/text()')
            if performers:
                performers = performers.getall()
                return list(map(lambda x: x.strip(), performers))
        else:
            performers = self.process_xpath(
                response, self.get_selector_map('performers')).get()
            if performers:
                performers = re.search(r'Starring(.*?)\*', performers).group(1)
                if performers:
                    performers = performers.replace("&amp;", "&")
                    performers = performers.split("&")
                    return list(map(lambda x: x.strip(), performers))
        return []

    def get_site(self, response):
        if 'teenlovesblack' in response.url:
            return "Teen Loves Black"
        elif 'wifelovesblack' in response.url:
            return "Wife Loves Black"
        else:
            return "Family Therapy XXX"
    
    def get_parent(self, response):
        return self.get_site(response)
    
    def get_network(self, response):
        return self.get_site(response)