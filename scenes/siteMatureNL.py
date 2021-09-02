import scrapy
import re
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteMatureNLSpider(BaseSceneScraper):
    name = 'MatureNL'
    network = 'Mature NL'
    start_urls = [
        'https://www.mature.nl',
    ]
    selector_map = {
        'title': r'//h1/text()',
        'description': r'//meta[@name="description"]/@content',
        'date': r'//div[@class="box-cnt"]/div[@class="mar-t"][1]/text()[1]',
        're_date': r'(\d{1,2}-\d{1,2}-\d{4})',
        'date_formats': [r'%d-%m-%Y'],
        'image': r'//span[@id="spnPageUpdateTrailer"]//img/@data-src',
        'performers':
            r'//div[@class="box-cnt"]//div[@class="grid-tile-model"]' \
            '/div[@class="name"]/span/text()',
        'tags': r'//div[@class="box-cnt"]' \
            '//a[contains(@href, "/niche/")]/text()',
        'external_id': r'update\/(\d+)\/',
        'trailer': r'//script[contains(text(),"showTrailer")]/text()',
        're_trailer': r'\"(http.*?\.mp4)\"',
        'pagination': '/en/updates/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            r'//div[@class="grid-item"]/div/a/@href').getall()
        for scene in scenes:
            if "/update/" in scene:
                try:
                    sceneid = re.search(r'\/update\/(\d+)', scene).group(1)
                except Exception:
                    print(scene)
            if "upid=" in scene:
                sceneid = re.search(r'upid=(\d+)', scene).group(1)
            scene = "https://www.mature.nl/en/update/" + sceneid.strip() + "/"

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene),
                            callback=self.parse_scene)

    def get_site(self, response):
        return "Mature NL"

    def get_parent(self, response):
        return "Mature NL"

    def get_performers(self, response):
        performers = super().get_performers(response)
        if performers:
            for i in range(len(performers)):
                performer = performers[i]
                if re.search(r'.*\(.*?\)', performer):
                    performer = re.sub(r'\(.*?\)', '', performer)
                performer = performer.strip()
                performers[i] = performer
        return performers

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            image = response.xpath(
                r'//div[@class="box-cnt"]//a[@class="mfp-image"]/@href'
            )
            if image:
                image = image.get().strip()
            else:
                image = ''
        return image

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = date.get()
        if not date or not re.search(r'(\d{1,2}-\d{1,2}-\d{4})', date):
            date = response.xpath(
                    r'//div[@class="container update-bg-container"]' 
                    '/div[@class="box"][1]/div[@class="box-cnt"]/div[1]')
            if date:
                date = date.get()
        if date and re.search(r'(\d{1,2}-\d{1,2}-\d{4})', date):
            date = self.get_from_regex(date, 're_date')
            if 'date_formats' in self.get_selector_map():
                date_formats = self.get_selector_map('date_formats')
            else:
                None
            return dateparser.parse(
                    date, date_formats=date_formats).isoformat()

    def get_title(self, response):
        title = super().get_title(response)
        if "watch this scene exclusively" in title.lower():
            newtitle = response.xpath(r'//div[@class="box-cnt"]' 
                    '//div[@class="grid-tile-model"]' 
                    '/div[@class="name"]/span/text()')
            if newtitle:
                newtitle = newtitle.getall()
                newtitle = " and ".join(newtitle)
                title = newtitle.strip()
        return title
