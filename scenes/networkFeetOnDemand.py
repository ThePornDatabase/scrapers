import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'feetpov': 'Feet POV',
        'goddessdomination': 'Goddess Domination',
        'jerktomyfeet': 'Jerk to My Feet',
        'goddessfootworship': 'Goddess Foot Worship',
        'goddessfootjobs': 'Goddess Footjobs',
        'goddessfootdomination': 'Goddess Foot Domination',
        'footfetishpetite': 'Foot Fetish Petite',
        'footslaveauditions': 'Foot Slave Auditions',
        'footfetishcardates': 'Foot Fetish Car Dates',
    }
    return match.get(argument, argument)


class NetworkFeetOnDemandSpider(BaseSceneScraper):
    name = 'FeetOnDemand'
    network = 'Feet On Demand'

    start_urls = [
        'https://www.feetondemand.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="row"]/div/p[2]/text()',
        'date': '//div[@class="row"]/div/p/small/text()',
        're_date': r'(\d{1,2} \w+ \d{4})',
        'date_formats': ['%d %B %Y'],
        'image': '//hr/following-sibling::div[1]/div[3]/img[1]/@src|//div[contains(@class,"carousel")]/div[1]/a/img/@src',
        'performers': '//a[contains(@href, "Models")]//text()',
        'tags': '//a[contains(@href, "Category")]//text()',
        'trailer': '',
        'external_id': r'mb=(.*)=',
        'pagination': '/index.php?mb=VmlkZW9zfHw=&clearcache=1&p=%s'
    }

    def get_next_page_url(self, base, page):
        page = (int(page) - 1) * 16
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        link = self.load_mainbody(response)
        if link:
            yield scrapy.Request(url=link, callback=self.get_scenes_from_index, meta=meta)

    def get_scenes_from_index(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "img-portfolio")]')
        for scene in scenes:
            image = scene.xpath('./a/img/@src')
            if image:
                meta['image'] = self.format_link(response, image.get())
            title = scene.xpath('./h4/a/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())
            site = scene.xpath('./p/a[contains(text(), "visit")]/text()')
            if site:
                site = site.get().lower().replace("visit", "").replace(".com", "").replace(" ", "").strip()
                meta['site'] = match_site(site)
                meta['parent'] = match_site(site)

            scene = scene.xpath('./a/@href').get()

            sceneid = re.search(r'mb=(.*)=', scene)

            if sceneid:
                meta['id'] = sceneid.group(1).strip()
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.load_scene, meta=meta)

    def load_scene(self, response):
        meta = response.meta
        link = self.load_mainbody(response)
        if link:
            yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = tags.copy()
        for tag in tags2:
            if ".com" in tag.lower():
                tags.remove(tag)
        return tags

    def load_mainbody(self, response):
        scenelist = response.xpath('//script[contains(text(), "#mainbody")]/text()')
        if scenelist:
            scenelist = scenelist.get()
            scenelist = re.search(r'(content/.*?\.htm)', scenelist).group(1)
            scenelist = f"https://www.feetondemand.com/{scenelist}"
            return scenelist
        return None

    def get_performers(self, response):
        performerlist = super().get_performers(response)
        performers = []
        for performer in performerlist:
            performer = performer.lower()
            if "goddess" in performer:
                wordcount = len(performer.split(" "))
                if wordcount > 2:
                    performer = performer.replace("goddess ", "")
            performers.append(string.capwords(performer))
        return performers
