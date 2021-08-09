import scrapy
import re
import string
import html
from tpdb.BaseSceneScraper import BaseSceneScraper


class networkPornRoleplaySpider(BaseSceneScraper):
    name = 'PornRoleplay'

    sites = [
        # ~ ['Defy XXX', 'Defy XXX', 'Defy XXX', '/tags/Defy%20XXX/page/{}/'],
        ['Blue Pill Men', 'Blue Pill Men', 'Blue Pill Men', '/tags/Blue%20Pill%20Men/page/{}/'],
        ['CFNM Show', 'CFNM Show', 'CFNM Show', '/tags/CFNM%20Show/page/{}/'],
        ['Cum Hogs', 'Cum Hogs', 'Cum Hogs', '/tags/Cum%20Hogs/page/{}/'],
        ['Dirty Coach', 'Dirty Coach', 'Dirty Coach', '/tags/Dirty%20Coach/page/{}/'],
        ['Dirty Doctor', 'Dirty Doctor', 'Dirty Doctor', '/tags/Dirty%Doctor/page/{}/'],
        ['Serious Coin', 'Gyno Lesbians', 'Gyno Lesbians', '/tags/Gyno%20Lesbians/page/{}/'],
        ['Serious Coin', 'Gyno Orgasm Videos', 'Gyno Orgasm Videos', '/tags/Gyno%20Orgasm%20Videos/page/{}/'],
        ['Horny in Hospital', 'Horny in Hospital', 'Horny in Hospital', '/tags/Horny%20In%20Hospital/page/{}/'],
        ['Horny Thief Tales', 'Horny Thief Tales', 'Horny Thief Tales', '/tags/Horny%20Thief%20Tales/page/{}/'],
        ['Lusty Office', 'Lusty Office', 'Lusty Office', '/tags/Lusty%20Office/page/{}/'],
        ['Russian Gynecology', 'Russian Gynecology', 'Russian Gynecology', '/tags/Russian%20Gynecology/page/{}/'],
        ['Shantibody Media', 'Shantibody Media', 'Shantibody Media', '/tags/Shantibody%20Media/page/{}/'],
        ['Serious Coin', 'Special Examination', 'Special Examination', '/tags/Special%20Examination/page/{}/'],
    ]
    
    url = 'https://pornroleplay.org'

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//b[contains(text(),"Description")]/following-sibling::text()',
        'date': '//time[@class="date"]/@datetime',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//b[contains(text(),"Model:")]/following-sibling::text()[1]',
        'tags': '//div[@class="text"]/div[@class="marbox20"][1]/div[@class="tag_list"]/span/a/text()',
        'external_id': '\/(\d+).*?.html',
        'trailer': '',
        'pagination': ''
    }
    

    def start_requests(self):
        link = self.url
        meta = {}
        for site in self.sites:
            meta['network'] = site[0]
            meta['parent'] = site[1]
            meta['site'] = site[2]
            meta['pagination'] = site[3]
            meta['page'] = self.page
            
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['pagination']),
                                 callback=self.parse,
                                 meta=meta,
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
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)             
                                     

    def get_next_page_url(self, base, page, pagination):
        url = self.format_url(base, pagination.format(page))
        print(f'URL: {url}')
        return url    

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2[@class="title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)


    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = title.get()
            site = response.meta['site']
            if re.search(f'(.*) - {site}', title):
                title = re.search(f'(.*) - {site}', title).group(1)
            title = title.lower()
            title = title.replace("sd","").replace("hd","").replace("wmv","").replace("mp4","").replace("mkv","").replace("4k","").replace("full hd","").replace("/","")
            title = title.strip()
            if title[-2:] == " -":
                title = title[:-2]
            
            return string.capwords(html.unescape(title.strip()))

        return None

    def get_tags(self, response):
        meta = response.meta
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = list(map(lambda x: x.strip().lower(), performers.getall()))        
        
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                tags = list(map(lambda x: x.strip().lower(), tags.getall()))
                
            if meta['site'].lower() in tags:
                tags.remove(meta['site'].lower())
                
            for performer in performers:
                if performer in tags:
                    tags.remove(performer)

            tags2 = tags.copy()
            for tag in tags2:
                matches = ['sd', 'mp4', 'hd', 'mkv']
                if any(x in tag.lower() for x in matches):
                    tags.remove(tag)                    
            
            tags = list(map(lambda x: x.strip().title(), tags))
            return tags
            

        return []
        
        


    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
            
        return tldextract.extract(response.url).domain


    def get_parent(self, response):
        meta = response.meta
        if meta['parent']:
            return meta['parent']
            
        return tldextract.extract(response.url).domain


    def get_network(self, response):
        meta = response.meta
        if meta['network']:
            return meta['network']
            
        return tldextract.extract(response.url).domain
        
