import re
import dateparser
import scrapy
import copy
from datetime import datetime, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

class AdultDVDEmpireMovieSpider(BaseSceneScraper):
    name = 'AdultDVDEmpireMovie'
    network = "Adult DVD Empire"

    start_urls = [
        'https://www.adultdvdempire.com'
    ]

    selector_map = {
        'title': '//div[contains(@class,"title-rating-section")]/div/h1/text()',
        'description': '//h4[contains(@class,"synopsis")]/p/text()',
        'date': '//li/small[contains(text(),"Released")]/following-sibling::text()',
        'image': '//link[@rel="image_src"]/@href',
        'performers': '//strong[contains(text(),"Starring")]/following-sibling::a/div/u/text()',
        'tags': '//strong[contains(text(),"Categories")]/following-sibling::a/text()',
        'external_id': '\/(\d+)\/',
        'trailer': '',
        'pagination': '/new-release-porn-movies.html?page=%s&media=2'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="product-card"]/div/a/@href').getall()
        for scene in scenes:
            scene = scene.strip()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)


    def get_parent(self, response):
        studio = response.xpath('//div[@class="item-info"]/a[@Label="Studio" or @label="Studio"]/text()').get()
        if studio:
            return studio.strip()
        else:
            return ""

    def get_site(self, response):
        site = response.xpath(
            '//div[contains(@class,"title-rating-section")]/div/h1/text()').get()
        if site:
            return "Movie: " + site.strip()
        else:
            return ""
            
            
    def get_description(self, response):

        description = response.xpath('//h4[contains(@class,"synopsis")]/p/text()|//h4[contains(@class,"synopsis")]/following-sibling::p/text()').get()

        if description is not None:
            return description.strip()
        return ""

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            tags.append("Movie")
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []


    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date.replace('Released:', '').replace('Added:', '').strip()
        else:
            date = response.xpath('//li/small[contains(text(),"Production")]/following-sibling::text()').get()
            if date:
                date = date + "-01-01"
            if not date:
                return datetime.now().isoformat()
                
        return dateparser.parse(date.strip()).isoformat()
        
        
    def parse_scene(self, response):
        item = SceneItem()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        else:
            item['parent'] = self.get_parent(response)


        moviescenes = response.xpath('//a[contains(@name,"scene") and @class="anchor"]/following-sibling::div[@class="row"]')
        if moviescenes:
            yield item
            for movie in moviescenes:
                newitem = SceneItem()
                newitem = copy.deepcopy(item)
                scenetitle = movie.xpath('./div/h3/a/text()').get()
                if scenetitle:
                    scenetitle = scenetitle.strip()
                    newitem['title'] = newitem['title'] + ": " + scenetitle
                    sceneperformers = movie.xpath('./div/div/a/text()')
                    sceneimage = movie.xpath('.//a[contains(@href,"caps1cdn.adultempire.com")]/@href').get()
                    # ~ print (f'image: {sceneimage}')
                    if sceneimage:
                        newitem['image'] = sceneimage.strip()
                    newitem['tags'] = []
                    newitem['description'] = []
                    if sceneperformers:
                        newitem['performers'] = sceneperformers.getall()
                    else:
                        newitem['performers'] = []
                    yield newitem
                    newitem.clear()
                    sceneimage = ""
                    sceneperformers.clear()
        else:
            if self.debug:
                print(item)
            else:
                yield item        
