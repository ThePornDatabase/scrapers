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
        ['https://www.manyvids.com', '/api/model/214657/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=60feafe6b5b83856828183', 'Manyvids: Lana Rain'],
        ['https://www.manyvids.com', '/api/model/423053/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=60feafe6b5b83856828183', 'MySweetApple'],
        ['https://www.manyvids.com', '/api/model/1001495638/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=60feafe6b5b83856828183', 'Manyvids: Jack and Jill'],
        ['https://www.manyvids.com', '/api/model/325962/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=60feafe6b5b83856828183', 'Manyvids: Dirty Princess'],
        ['https://www.manyvids.com', '/api/model/312711/videos?category=all&offset=%s&sort=0&limit=30&mvtoken=60feafe6b5b83856828183', 'Manyvids: Cattie'],
    ]
    
    selector_map = {
        'title': '',
        'description': '//div[@class="desc-text"]/text()',
        'date': '//div[@class="mb-1"]/span[2]/text()',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '',
        'tags': '//script[contains(text(),"tagListApp")]/text()',
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
                     callback=self.get_taglist,
                     headers=self.headers,
                     cookies=self.cookies)     
                     
    def get_taglist(self, response):
        meta=response.meta
        url = "https://d3e1078hs60k37.cloudfront.net/site_files/json/vid_categories.json"
        yield scrapy.Request(url,
                     callback=self.start_requests2,
                     headers=self.headers,
                     cookies=self.cookies, meta=meta)     

    def start_requests2(self, response):
        meta=response.meta
        taglist = json.loads(response.text)
        meta['taglist'] = taglist
       
        for link in self.start_urls:
            meta['page'] = self.page
            meta['pagination'] = link[1]
            meta['site'] = link[2]
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
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
        meta = response.meta
        global json
        jsondata = json.loads(response.text)
        data = jsondata['result']['content']['items']
        for jsonentry in data:
            scene = "https://www.manyvids.com" + jsonentry['preview']['path'].replace("\\","")
            if jsonentry['preview']['videoPreview']:
                meta['trailer'] = jsonentry['preview']['videoPreview'].replace("\\","").replace(" ","%20")
            meta['id'] = jsonentry['id']
            meta['title'] = jsonentry['title']
            if scene and meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)                   




    def get_date(self, response):
        meta=response.meta
        imagestring = response.xpath('//meta[@name="twitter:image"]/@content').get()
        if imagestring:
            imagestring = re.search('.*_([0-9a-zA-Z]{10,20}).jpg', imagestring)
            if imagestring:
                imagestring = imagestring.group(1)
                imagestringhex = imagestring[:8]
                if imagestringhex and "386D43BC" <= imagestringhex <= "83AA7EBC":
                    imagedate = int(imagestringhex, 16)
                    date = datetime.utcfromtimestamp(imagedate).isoformat()
                    return date
                if imagestring and 946684860 <= int(imagestring) <= 2208988860:
                    date = datetime.utcfromtimestamp(int(imagestring)).isoformat()
                    return date

                
        # If no valid image string available to pull date from
        #print(f'Guessing date for: {response.url}')
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
                
                sceneid = re.search('Video\/(\d+)\/', response.url).group(1)
                if sceneid:
                    sceneid = int(sceneid)
                    if sceneid > 2462280:
                        scenedate = scenedate + "2021"
                    if 1657000 <= sceneid <= 2462279:
                        scenedate = scenedate + "2020"                
                    if 1014000 <= sceneid <= 1656999:
                        scenedate = scenedate + "2019"                
                    if 600000 <= sceneid <= 1013999:
                        scenedate = scenedate + "2018"
                    if sceneid < 599999:
                        scenedate = scenedate + "2017"
                else:
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
        meta = response.meta
        if meta['site'] == "Lana Rain":
            return ['Lana Rain']
        if meta['site'] == "Cattie":
            return ['Cattie Candescent']
        
        return []
        
    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        else:
            return "Manyvids"
        
    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            if "Manyvids" in meta['site']:
                return "Manyvids"
            return meta['site']
        else:
            return "Manyvids"
        
    def get_network(self, response):
        return "Manyvids"
            

    def get_tags(self, response):
        meta = response.meta
        taglist = meta['taglist']
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags')).get()
            if tags:
                tags = re.search('\"(.*)\"', tags).group(1)
                if tags:
                    tags = tags.split(",")
                    scenetags = []
                    for tag in tags:
                        for alltags in taglist:
                            if alltags['id'] == tag:
                                scenetags.append(alltags['label'])
                                break
            if meta['site'] and "ManyVids" in meta['site']:
                scenetags.append("ManyVids")
            if scenetags:
                return list(map(lambda x: x.strip().title(), scenetags))

        return []            
