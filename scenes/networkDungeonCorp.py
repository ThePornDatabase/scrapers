import scrapy
import re
import html
import string
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy import Selector


class networkDungeonCorpSpider(BaseSceneScraper):
    name = 'DungeonCorp'
    network = 'Dungeon Corp'


    start_urls = [
        'http://dungeoncorp.com',
    ]

    selector_map = {
        'title': '//div[@class="heading"]/text()[1]',
        're_title': '\"(.*)\"',
        'description': '//div[@class="descriptext"]//text()|//span[contains(@class,"descript") and not(.//object) and not(contains(.//text(),"FREE VIDEO")) and not(contains(@class,"descriptext1"))]//text()|//p[contains(@class,"descript")]//text()|//td[contains(@class,"descrip")]//text()',
        'date': '',
        'image': '//img[contains(@src,"vidt1.jpg")]/@src|//img[contains(@src,"vidt.jpg")]/@src',
        'performers': '',
        'tags': '//td[contains(text(),"Categories")]/following-sibling::td/a/text()',
        'external_id': 'id=(\d+)',
        'trailer': '',
        'pagination': '/trial/index.php?page=%s'
    }
    

    def start_requests(self):
        
        url = "http://dungeoncorp.com/NEWS/updates_guest_all.js"
        yield scrapy.Request(url, callback=self.get_scenes,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)    

    def get_scenes(self, response):
        meta = response.meta
        
        javascript = response.text
        counter = 0
        pagelimit = 10
        if self.limit_pages:
            if self.limit_pages == "all":
                pagelimit = 9999
            else:
                pagelimit = int(self.limit_pages) * 10
        for line in javascript.split("\r\n"):
            if "<td>" in line.lower() and "javascript" not in line.lower() and "updates.html" not in line.lower() and "http://join." not in line.lower():
                counter += 1
                if counter <= pagelimit:

                    line_text = re.search('write\(\"(.*)\"\)', line)
                    if line_text:
                        line_text = line_text.group(1)
                        line_text = html.unescape(line_text)
                        line_text = line_text.replace("\\","")
                        line_sel = Selector(text=line_text)

                        scene = line_sel.xpath('//a/@href').get()
                        meta['id'] = re.search('.*\/(.*?)\/.*?$', scene).group(1)
                        meta['orig_image'] = line_sel.xpath('//img/@src').get().strip()
                        meta['site'] = line_sel.xpath('//span[@class="sitename"]/text()').get().strip()
                        date = line_sel.xpath('//span[@class="date"]/text()').get().strip()
                        meta['date'] = dateparser.parse(date, date_formats=['%m.%d.%Y']).isoformat()
                        performers = line_sel.xpath('//span[@class="modelname"]/text()').get()
                        if "and" in performers.lower():
                            performers = performers.split(" and ")
                        else:
                            performers = [performers]
                        meta['performers'] = list(map(lambda x: x.replace("  "," ").strip(), performers))
                        
                        yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)                    
        
                
                
    def get_date(self, response):
        return dateparser.parse('today').isoformat()
        
    def get_title(self, response):
        title = response.xpath('//span[@class="shoottitle"]//text()')
        if not title:
            title = response.xpath('//div[@class="heading"]/text()[1]')
        if not title:
            title = response.xpath('//td[@class="heading"]/text()[1]')
        if not title:
            title = response.xpath('//*[contains(text(),"Preview for")]/text()')
        if not title:
            title = response.xpath('//*[contains(text(),"Preivew for")]/text()')
        if not title:
            title = response.xpath('//*[contains(text(),"Preview") and contains(text(),"for")]/text()')
            
        if title:
            title = title.getall()
            title = "".join(title)

        if '"' in title:
            titlestrip = re.search('\"(.*)\"', title)
            if titlestrip:
                title = titlestrip.group(1)
                # ~ print(title)

        if title:
            return title.strip()
        else:
            return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = image.get()
            image = image.replace("..","")
            if "vidt1.jpg" in image:
                image = response.url.replace("index.html","vidt1.jpg").replace("index.php","vidt1.jpg")
            if "vidt.jpg" in image:
                image = response.url.replace("index.html","vidt.jpg").replace("index.php","vidt.jpg")
                
            image = self.format_link(response, image)
            return image.replace(" ", "%20")
        else:
            return response.meta['orig_image']

    def get_performers(self, response):
        return []
        
    def get_tags(self, response):
        return ['Bondage', 'Submission']
        
    def get_parent(self, response):
        return response.meta['site']
        

    def get_description(self, response):
        if 'description' not in self.get_selector_map():
            return ''

        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = "".join(description)
            description = description.replace("\r","").replace("\n","").replace("\t","")
            return html.unescape(description.strip())

        return ''
