import scrapy
from chompjs import chompjs
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from extruct.jsonld import JsonLdExtractor
import tldextract
import re



class GammaEnterprisesSpider(BaseSceneScraper):
    name = 'GammaEnterprises'
    network = 'GammaEnterprises'

    start_urls = [
        'https://www.blowpass.com',
        # ~ 'https://www.1000facials.com',
        # ~ 'https://www.immorallive.com',
        # ~ 'https://www.mommyblowsbest.com',
        # ~ 'https://www.onlyteenblowjobs.com',
        # ~ 'https://www.throated.com',
        
        'https://www.21naturals.com/',
        'https://www.21sextreme.com/',
        'https://www.bskow.com',
        'https://www.buttman.com',
        'https://www.devilsfilm.com',
        'https://www.dpfanatics.com',
        'https://www.falconstudios.com',

        'https://www.fantasymassage.com',
        # ~ 'https://www.allgirlmassage.com',
        # ~ 'https://www.nurumassage.com',
        
        'https://www.footsiebabes.com',
        'https://www.girlfriendsfilms.com',
        'https://www.girlsandstuds.com/',
        'https://www.jaysinxxx.com',
        'https://www.jonnidarkkoxxx.com',
        'https://www.outofthefamily.com',
        'https://www.peternorth.com',
        'https://www.prettydirty.com',
        'https://www.roccosiffredi.com',
        'https://www.ragingstallion.com',
        
        'https://www.xempire.com',
        # ~ 'https://www.allblackx.com/',
        # ~ 'https://www.darkx.com/',
        # ~ 'https://www.eroticaX.com/',
        # ~ 'https://www.hardx.com/',
        # ~ 'https://www.lesbianx.com/',
    ]

    selector_map = {
        'title': '//h1[@class="sceneTitle"]/text() | //h3[@class="sceneTitle"]/text() | //h1[@class="seo_h1"]/text() | //h1[@class="title"]/text() | //h3[@class="dvdTitle"]/text() | //h1[@class="dynamicContent"]/text()',
        'description': "//meta[@itemprop='description']/@content | //*[@class='p-desc']/text()",
        'date': '//div[@class="tlcSpecs"]/span[@class="tlcSpecsDate"]/span[@class="tlcDetailsValue"]/text() | //*[@class="updatedDate"]/text()',
        'image': '//meta[@name="twitter:image"]/@content | //video/@poster | //meta[@property="og:image"]/@content | //div[@class="module-content"]//img[contains(@src,"/previews/")]/@src',
        'performers': '//div[@class="sceneCol sceneColActors"]//a/text() | //p[@class="starringLinks"]//a/text() | //div[@class="sceneCol actors"]//a/text() | //div[@class="actors sceneCol"]//a/text() | //div[@class="sceneCol sceneActors"]//a/text() | //div[@class="pornstarName"]/text() | //a[@class="pornstarName"]/text() | //div[@id="slick_DVDInfoActorCarousel"]//a/text() | //div[@id="slick_sceneInfoPlayerActorCarousel"]//a/text() | //div[@id="slick_sceneInfoActorCarousel"]//a/text()',
        'tags': "",
        'external_id': '(\\d+)/?$',
        'trailer': '',
    }

    def get_scenes(self, response):
        selectors = [
            "//div[@class='content']/ul[@class='sceneList']/li[contains(@class,'scene')]//a[contains(@class,'imgLink')]/@href",
            "//ul[@class='sceneList']/li[contains(@class,'sceneItem')]//a[contains(@class,'imgLink')]/@href",
            "//div[@class='tlcAllContentHolder']//div[@class='tlcContent']//div[contains(@class, 'tlcContent')]//div[contains(@class, 'tlcItem')]/a[1]/@href",
            "//div[@class='sceneContainer']/a/@href",
        ]
        
        if "fantasymassage" in response.url:
            scenes = response.xpath("//div[@class='tlcAllContentHolder']//div[@class='tlcContent']//div[contains(@class, 'tlcContent')]//div[contains(@class, 'tlcItem')]")
        else:
            scenes = response.xpath(' | '.join(selectors)).getall()
            
        for scene in scenes:
            
            if "fantasymassage" in response.url:
                site = scene.xpath('.//div[@class="tlcSourceSite"]/span/a/text()').get().strip()
                scene = scene.xpath('./a[1]/@href').get().strip()
            
            if "fantasymassage" in response.url and site:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site':site})
            else:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
                

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
            
        if "bskow" in response.url or "footsiebabes" in response.url:
            image = response.xpath('//script[contains(text(),"picPreview")]').get()
            image = re.search('picPreview\":\"(.*?)\",',image).group(1).strip()
            image = image.replace('\\','')
            
        if image is not None:
            return self.format_link(response, image)

    def parse_scene(self, response):
        data = response.css('script:contains("dataLayer =")::text').get()
        json_data = chompjs.parse_js_object(data)[0]

        jslde = JsonLdExtractor().extract(response.text)
        jsonlde = {}
        for obj in jslde:
            jsonlde.update(obj)

        item = SceneItem()

        if 'sceneDetails' in json_data and 'sceneTitle' in json_data['sceneDetails']:
            item['title'] = json_data['sceneDetails']['sceneTitle']
        elif 'name' in jsonlde:
            item['title'] = jsonlde['title']
        else:
            item['title'] = self.get_title(response)

        if 'sceneDetails' in json_data and 'sceneDescription' in json_data['sceneDetails']:
            item['description'] = json_data['sceneDetails']['sceneDescription']
        elif 'description' in jsonlde:
            item['description'] = jsonlde['description']
        else:
            item['description'] = self.get_description(response)

        item['site'] = self.get_site(response)

        if item['site'] is None and 'siteName' in json_data:
           item['site'] = json_data['siteName']

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        elif 'dateCreated' in jsonlde:
            item['date'] = jsonlde['dateCreated']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        elif 'actor' in jsonlde:
            item['performers'] = list(map(lambda x: x['name'].strip(), jsonlde['actor']))
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        elif 'keywords' in jsonlde:
            item['tags'] = jsonlde['keywords'].split(',')
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
            item['parent'] = self.network
        else:
            item['parent'] = self.get_network(response)            

        if self.debug:
            print(item)
        else:
            return item

    def get_next_page_url(self, base, page):
        selector = '/en/videos/AllCategories/0/%s'

        if 'prettydirty' in base:
            selector = '/en/videos/updates/%s/Category/0/Pornstar/0'

        if 'girlfriendsfilms' in base:
            selector = '/en/videos/all-series/0/all-categories/0/all-pornstars/0/latest/%s'

        if 'peternorth' in base:
            selector = '/en/videos/All-Categories/0/All-Pornstars/0/All-Dvds/0/latest/%s'

        if 'outofthefamily' in base:
            selector = '/en/videos/latest/All-Categories/0/All-Pornstars/0/All-Dvds/0/%s'
            
        if 'roccosiffredi' in base:
            selector = '/en/videos/latest/%s'

        if 'onlyteenblow' in base or 'mommyblowsbest' in base:
            selector = '/en/scenes/updates/0/Category/0/Actor/%s'

        if 'blowpass' in base or 'allgirlmassage' in base:
            selector = '/en/videos/blowpass/latest/All-Categories/0/All-Pornstars/0/%s'

        if 'falconstudios' in base:
            selector = '/en/videos/latest/All+Categories/0/All+Models/0/All+Dvds/0/Falcon+Studios//%s'

        if 'allgirlmassage' in base or 'nurumassage' in base:
            selector = '/en/videos/updates/All-Categories/0/All-Pornstars/0/%s'

        if 'devilsfilm' in base:
            selector = '/en/scenes/AllCategories/0/%s'
        
        if 'xempire' in base:
            selector = '/en/videos/xempire/latest/%s'
        
        if 'ragingstallion' in base:
            selector = '/en/scenes/All+Studios/0/%s'

        if 'jaysinxxx' in base or 'jonnidarkkoxxx' in base:
            selector = '/en/scenes/All/0/latest/%s'

        if 'girlsandstuds' in base:
            selector = '/en/allfilms/latest/%s'

        if '21sextreme' in base:
            selector = '/en/videos/updates/%s/categoryName/0/Pornstar/0'
                                                
        if '21naturals' in base:
            selector = '/en/videos/%s'
                                                
        if 'bskow' in base:
            selector = 'en/videos/updates/%s/All/0/Pornstar/0'
                                                
        if 'fantasymassage' in base:
            selector = '/en/videos/AllCategories/0/Actor/0/updates/%s'
                                                
        if 'buttman' in base:
            selector = '/en/scenes/All/0/%s'
                                                
        if 'footsiebabes' in base:
            selector = '/en/videos/All-Categories/0/All-Pornstars/0/latest/%s'
                                                
        return self.format_url(base, selector % page)

    def get_site(self, response):

        if 'site' in response.meta:
            return response.meta['site']
            
        if response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()'):
            return response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()').get().strip().split('.')[0]

        if response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()'):
            return response.xpath(
                '//span[@class="fromCaption"]/following-sibling::a/strong/text()').get().strip().split('.')[0]
                        
        if response.xpath('//meta[@name="twitter:domain"]'):
            return response.xpath(
                '//meta[@name="twitter:domain"]/@content').get().replace('www.', '').split('.')[0]
                
        if response.xpath(
                '//div[@class="siteLink"]//a/text() | //div[@id="videoInfoTop"]//a/text()'):
            return response.xpath(
                '//div[@class="siteLink"]//a/text() | //div[@id="videoInfoTop"]//a/text()').get().strip()

                
        if response.css('span.siteNameSpan') is not None:
            return response.css('span.siteNameSpan::text').get()
            
        return tldextract.extract(response.url).domain


                
                
