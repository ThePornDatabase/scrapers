import scrapy
import re
import dateparser
from datetime import datetime
from time import strptime
import tldextract
import json
from urllib.parse import urlparse

from tpdb.BaseSceneScraper import BaseSceneScraper

class networkManyVidsSpider(BaseSceneScraper):
    name = 'ManyVids'

    start_urls = [
        ['https://www.manyvids.com', '/api/model/1001216419/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=60feafe6b5b83856828183', 'YouthLust'],
    ]
    
    selector_map = {
        'title': '',
        'description': '//div[@class="desc-text"]/text()',
        'date': '//div[@class="mb-1"]/span[2]/text()',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '',
        'tags': '//a[contains(@href,"?category")]//text()',
        'external_id': '',
        'trailer': '',
        'pagination': ''
    }

    headers =  {
        'X-Requested-With': 'XMLHttpRequest'
    }

    cookies =  {
        'PHPSESSID': 'UbKPmgIeKncVZqtCq8b49KU1ePIzWPnFEMT0USVo'
    }
    

    def start_requests(self):
        url = "https://www.manyvids.com/Profile/1001216419/YouthLust/Store/Videos/"
        yield scrapy.Request(url,
                     callback=self.start_requests2,
                     headers=self.headers,
                     cookies=self.cookies)        

    def start_requests2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination':link[1], 'site':link[2]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        offset = str((int(page)-1)*30)
        return self.format_url(base, pagination % offset)                                

    def get_scenes(self, response):
        global json
        jsondata = json.loads(response.text)
        data = jsondata['result']['content']['items']
        for jsonentry in data:
            meta = response.meta
            scene = "https://www.manyvids.com" + jsonentry['preview']['path'].replace("\\","")
            if jsonentry['preview']['videoPreview']:
                meta['trailer'] = jsonentry['preview']['videoPreview'].replace("\\","")
            meta['id'] = jsonentry['id']
            meta['title'] = jsonentry['title']
            if scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)                   




    def get_date(self, response):
        meta=response.meta
        page = int(meta['page'])
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date = date.strip()
            if re.search('([a-zA-Z]{3} \d{1,2})', date):
                date = re.search('([a-zA-Z]{3} \d{1,2})', date).group(1)
                date = date.split(" ")
                monthstring = datetime.strptime(date[0],'%b')
                month = str(monthstring.month)
                if len(month) == 1:
                    month = "0" + month
                if len(date[1]) == 1:
                    day = "0" + date[1]
                else:
                    day = date[1]
                
                today = datetime.now().strftime('%m%d')
                year = datetime.now().strftime('%Y')
                scenedate = str(month) + str(day)
                if page >= 1 and page <= 5:
                    if scenedate <= today:
                        scenedate = scenedate + year
                    else:
                        scenedate = scenedate + str(int(year)-1)
                        
                if page >= 6 and page <= 7:
                    if scenedate <= today:
                        scenedate = scenedate + str(int(year)-1)
                    else:
                        scenedate = scenedate + str(int(year)-2)
                        
                if page == 8:
                    if scenedate <= today:
                        scenedate = scenedate + str(int(year)-2)
                    else:
                        scenedate = scenedate + str(int(year)-3)
                        
                if page == 9:
                    if scenedate <= today:
                        scenedate = scenedate + str(int(year)-3)
                    else:
                        scenedate = scenedate + str(int(year)-4)
                        
                if page == 10:
                    if scenedate <= today:
                        scenedate = scenedate + str(int(year)-4)
                    else:
                        scenedate = scenedate + str(int(year)-5)
                        
                if page > 10:
                    if scenedate <= today:
                        scenedate = scenedate + str(int(year)-5)
                    else:
                        scenedate = scenedate + str(int(year)-6)
                        

            if len(scenedate)>2:
                try:
                    return dateparser.parse(scenedate, date_formats=['%m%d%Y']).isoformat()
                except:
                    return dateparser.parse('today').isoformat()

        return None


    def get_performers(self, response):
        return []
        
    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        else:
            return "ManyVids"
        
    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        else:
            return "ManyVids"
            
