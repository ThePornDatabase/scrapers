import scrapy
import re
import datetime
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.http import FormRequest

class FrolicMeSpider(BaseSceneScraper):
    name = 'FrolicMe'
    network = 'Frolic Me'
    parent = 'Frolic Me'

    start_urls = [
        'https://www.frolicme.com/',
    ]

    selector_map = {
        'title': '//div[@class="film-entry-title"]/text()',
        'description': '//div[@class="film-content"]/p/text()|//div[@class="film-content"]/p/span/text()|//div[@class="film-content"]/div/p/text()',
        'date': '//script[contains(text(), "datePublished")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h3/a[contains(@href,"/models/")]/text()',
        'tags': '//i[contains(@class,"fa-tags")]/following-sibling::a/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '',
        'pagination': '/publications/page/%s/'
    }


    def start_requests(self):
        frmheaders = {}
        frmheaders['Content-Type'] = 'application/x-www-form-urlencoded'
        frmdata = {"dob": "1995-05-09", "country": "RU"}
        url = "https://www.frolicme.com/wp-json/frolic/v1/verify"
        yield FormRequest(url, headers=frmheaders, formdata=frmdata)      

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)


    def get_scenes(self, response):
        scenes = response.xpath('//article[contains(@class,"cpt_films")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "FrolicMe"
        
    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title')).get()
        title = title.lower()
        title = title.replace('- film', '')
        if title:
            return title.strip().title()
        return ''


    def get_description(self, response):
        description = self.process_xpath(
            response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return description.strip()

        return ""
        
    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date = re.search('datePublished\": ?\"(\d{4}-\d{2}-\d{2}.*?)\"', date).group(1)
            if date:
                return date.strip()

        return datetime.now().isoformat()

