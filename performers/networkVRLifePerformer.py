import scrapy

from scrapy.http import HtmlResponse

from extruct.jsonld import JsonLdExtractor
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem

class networkVRLifePerformerSpider(BasePerformerScraper):
    name = 'VRLifePerformer'
    network = 'VRLife'
    parent = 'VRLife'
    start_urls = [
        'https://virtualrealporn.com',
        'https://virtualrealtrans.com',
        'https://virtualrealpassion.com',
        'https://virtualrealgay.com',
        'https://virtualrealamateurporn.com',
    ]


    selector_map = {
        'url': '//div[@class="performerItem"]//a[contains(@href, "/vr-pornstars/") or contains(@href, "/vr-models/")]/@href',
        'external_id': r'\/vr-models\/(.*)\/$',
        'date_formats': ['%d/%m/%Y'],
    }

    def start_requests(self):
        for link in self.start_urls:
            url = f"{link}/wp-admin/admin-ajax.php"
            headers = self.headers
            headers['Content-Type'] = 'application/x-www-form-urlencoded'    
            body = self.create_post_data(self.page)
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 method="POST",
                                 body=body,
                                 meta={'page': self.page},
                                 headers=headers,
                                 cookies=self.cookies)    
    
    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                body = self.create_post_data(meta['page'])
                headers=self.headers
                headers['Content-Type'] = 'application/x-www-form-urlencoded'    
                
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     method="POST",
                                     body=body,
                                     headers=headers,
                                     cookies=self.cookies)

    def create_post_data(self, page):
        return f"action=virtualreal_get_performers&sort=rating&sortDirection=DESC&index={(page-1)}&itemsPerPage=15"

    def get_performers(self, response):

        jsondata = response.json()['performers']
        for jsonrow in jsondata:
            response = HtmlResponse(url=response.url, body=jsonrow, encoding='utf-8')
            url = self.process_xpath(response, self.get_selector_map('url')).get()
            yield scrapy.Request(url=self.format_link(response, url), callback=self.parse_performer)


    def parse_performer(self, response):
        jslde = JsonLdExtractor()
        json = jslde.extract(response.text)
        data = {}
        for obj in json:
            if '@type' in obj and obj['@type'] == 'Person':
                data = obj
                break

        bio_data = self.parse_bio_data(response)
        for key in bio_data:
            if not key in ["Gender","Date of birth","Country","Eyes color","Hair color","Bust","Waist","Hips","Piercing","Tattoo","Penis size","Blog / Web"]:
                raise Exception(f"{key} not found")

        item = PerformerItem()
        item['url'] = response.url
        item['network'] = self.network

        item['name'] = data['name']
        if 'image' in data:
            item['image'] = data['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])      
        
        if 'description' in data:
            item['bio'] = self.cleanup_description(data['description'])

        if 'Gender' in bio_data:
            item['gender'] = bio_data['Gender']

        if 'Date of birth' in bio_data:
            try:
                date_formats = self.get_selector_map('date_formats')
                item['birthday'] = self.parse_date(self.cleanup_text(bio_data['Date of birth']), date_formats=date_formats).isoformat()            
            except:
                item['birthday'] =''

        if 'Country' in bio_data:
            item['birthplace'] = bio_data['Country']

        if 'Eyes color' in bio_data:
            item['eyecolor'] = bio_data['Eyes color']

        if 'Hair color' in bio_data:
            item['haircolor'] = bio_data['Hair color']

        bust = ""
        if "Bust" in bio_data and bio_data['Bust'] != "0":
            try:
                bust = round(int(bio_data['Bust']) / 2.54)
            except:
                bust = "?"
        else:
            bust = "?"


        # Measurements are in EU sizes, converting to US
        measurements = ''
        waist = ""
        if "Waist" in bio_data and bio_data['Waist'] != "0":
            try:
                waist = round(int(bio_data['Waist']) / 2.54)      
            except:
                waist = "?"                      
        else:
            waist = "?"

        hips = ""
        if "Hips" in bio_data and bio_data['Hips'] != "0":
            try:
                hips = round(int(bio_data['Hips']) / 2.54)         
            except:
                hips = "?"
        else:
            hips = "?"

        if not (bust == "?" and waist == "?" and hips == "?"):
            measurements = str(bust) + "-" + str(waist) + "-" + str(hips)

        item['measurements'] = measurements
        
        if 'Tattoo' in bio_data:
            item['tattoos'] = bio_data['Tattoo']

        if 'Piercing' in bio_data:
            item['piercings'] = bio_data['Piercing']

        for i in ['astrology','height','weight','cupsize','fakeboobs','nationality','ethnicity']:
            item[i] = ''
        
        yield item        


    def parse_bio_data(self, response):
        # Bio data available in simple table, zipping to create dictionary of all available data
        items = response.css('#table_about tbody th').xpath("normalize-space()").getall()
        values = response.css('#table_about tbody td').xpath("normalize-space()").getall()
        if len(items) != len(values):
            raise Exception("Can't parse Actor details")
        
        return dict(zip(items,values))                
