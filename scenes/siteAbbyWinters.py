import dateparser
import scrapy
import re
from tpdb.BaseSceneScraper import BaseSceneScraper


## Note: Images and Trailers include expiry tokens.  Only useful for time of import

class AbbyWintersSpider(BaseSceneScraper):

    name = 'AbbyWinters'
    network = 'Abby Winters'
    parent = 'Abby Winters'


    custom_settings = {'CONCURRENT_REQUESTS': '4',
                        'AUTOTHROTTLE_ENABLED': 'True',
                        'AUTOTHROTTLE_DEBUG': 'False',
                        'ITEM_PIPELINES': {
                                'tpdb.pipelines.TpdbApiScenePipeline': 400,
                            },
                            'DOWNLOADER_MIDDLEWARES': {
                                'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
                            }
                        }

    start_urls = [
        'https://www.abbywinters.com'
    ]

    selector_map = {
        'title': '//div[@class="container"]/h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//li/i[@class="icon-eye-open"]/following-sibling::span/following-sibling::text()',
        'image': '//div[@class="feature-image"]/div/img/@src',
        'imagealt': '//div[contains(@class,"video-player-container")]/@data-poster',
        'performers': '//table[@class="table table-summary"]//th[contains(text(),"Girls in this Scene")]/following-sibling::td/a/text()',
        'tags': '//a[contains(@href,"/fetish/")]/text()',
        'external_id': 'abbywinters\.com\/(.*)',
        'trailer': '//div[contains(@class,"video-player-container")]/@data-sources',
        'pagination': '/updates/raves?page=%s'
    }
            
    def get_scenes(self, response):
        scenes = response.xpath('//span[@class="icon_videoclip"]/../..')
        for scene in scenes:
            date = scene.xpath('./h2/span[contains(text()," 20")]/text()').get()
            date = dateparser.parse(date.strip()).isoformat()
            
            scene = scene.xpath('./div[@class="thumb"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})            

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        search = search.group(1).replace("/","-")
        
        return search


    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
        if not image:
            image = self.process_xpath(
                response, self.get_selector_map('imagealt')).get()
        return self.format_link(response, image)


    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(
                response, self.get_selector_map('trailer')).get()            
            if trailer:
                trailer = re.search('.*src\":\"(https.*?)\",', trailer).group(1).replace("\\","")
                return trailer
        return ''
        
    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []        

    def get_site(self, response):
        return "Abby Winters"
