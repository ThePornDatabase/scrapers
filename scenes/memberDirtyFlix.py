import scrapy
import re
import calendar
import time
import html
import json
from scrapy.http import FormRequest
from scrapy import Selector

# Member site: call with "-a user=xxxxxxx -a password=xxxxxxxxx"


from tpdb.BaseSceneScraper import BaseSceneScraper

def match_site(argument):
    match = {
        '28': "Brutal X",
        '33': "Debt Sex",
        '21': "Disgrace That Bitch",
        '4': "Fucking Glasses",
        '32': "Kinky Family",
        '18': "Make Him Cuckold",
        '30': "Massage X",
        '14': "Moms Passions",
        '22': "Private Casting X",
        '5': "She Is Nerdy",
        '31': "Spy POV",
        '23': "Trick Your GF",
        '7': "Tricky Agent",
        '27': "X Sensual",
        '19': "Young Courtesans",
    }
    return match.get(argument, argument)


class networkDirtyFlixSpider(BaseSceneScraper):
    name = 'DirtyFlix'
    network = 'DirtyFlix'


    start_urls = [
        'https://members.dirtyflix.com/',
    ]

    def start_requests(self):
    
        url = "https://members.dirtyflix.com/en/"
        yield scrapy.Request(url, callback=self.start_requests2,
                             headers=self.headers,
                             cookies=self.cookies)        
        
    def start_requests2(self, response):
        csrf = response.xpath('//input[@id="signin__csrf_token"]/@value').get()
        if csrf:
            user = self.user
            password = self.password
            frmheaders = {}
            frmheaders['Content-Type'] = 'application/x-www-form-urlencoded'
            frmdata = {"signin[username]": user, "signin[password]": password,"signin[_csrf_token]":csrf}
            url = "http://members.dirtyflix.com/en/support"
            yield FormRequest(url, headers=frmheaders, formdata=frmdata, callback=self.start_requests_actual, cookies=self.cookies)
            
    def start_requests_actual(self, response):
        epochtime = str(int(time.time()))
        headers = self.headers
        headers['Referer'] = "http://members.dirtyflix.com/en/browse/movies/?source=29&order=id"
        headers['X-Requested-With'] = "XMLHttpRequest"
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                             meta={'page': self.page},
                             headers=headers,
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
                print('NEXT PAGE: ' + str(meta['page']))
                headers = self.headers
                headers['Referer'] = "http://members.dirtyflix.com/en/browse/movies/?source=29&order=id"
                headers['X-Requested-With'] = "XMLHttpRequest"                
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=headers,
                                     cookies=self.cookies)
        
    selector_map = {
        'title': '//div[@class="entry-container"][1]/div[@class="icon top"]/div[@class="title"]/h3/text()',
        'description': '//div[@class="movie-info"]/div[@class="text"]/p/text()',
        'date': '//div[@class="movie-info"]/div[@class="text"]/div[@class="date"]/text()',
        're_date': 'Added: (.*)',
        'date_formats': ['%b %d, %Y'],
        'image': '//script[contains(text(),"playerInstance")]/text()',
        're_image': 'image: \"(http.*?.jpg)\"',
        'performers': '//div[@class="model"]/a/text()',
        'tags': '//div[@class="tags" or @class="categories"]/a/text()',
        'external_id': 'watch\/(\d+)\/',
        'trailer': '',
        'pagination': '/en/browse/filtrate?page={}&view=short&quality=all&source=all&studio=all&serie=all&order=date&ipp=12&_={}'
        # ~ 'pagination': '/en/browse/filtrate?page={}&view=short&quality=all&source=all&studio=all&serie=all&order=date&ipp=40&_={}'
    }

    def get_scenes(self, response):
        if "html" in response.text:
            global json
            jsondata = json.loads(response.text)
            data = jsondata['html']
            data = html.unescape(data)
            sel = Selector(text=data)
            scenes = sel.xpath('//div[@class="image dfRotate"]/a/@href').getall()
            for scene in scenes:
                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)


    def get_next_page_url(self, base, page):
        epochtime = str(int(time.time()))
        return self.format_url(base, self.get_selector_map('pagination').format(page, epochtime))

        
    def get_site(self, response):
        sitenum = response.xpath('//div[@class="movie-info"]/a[@class="site"]/@href')
        if sitenum:
            sitenum = sitenum.get()
            sitenum = re.search('source=(\d+)', sitenum)
            if sitenum:
                sitenum = sitenum.group(1)
                site = match_site(str(sitenum.strip()))
                if site:
                    return site
        return "Dirty Flix"
        
    def get_parent(self, response):
        sitenum = response.xpath('//div[@class="movie-info"]/a[@class="site"]/@href')
        sitenum = response.xpath('//div[@class="movie-info"]/a[@class="site"]/@href')
        if sitenum:
            sitenum = sitenum.get()
            sitenum = re.search('source=(\d+)', sitenum)
            if sitenum:
                sitenum = sitenum.group(1)
                site = match_site(str(sitenum.strip()))
                if site:
                    return site
        return "Dirty Flix"
            
