import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class IFeelMyselfSpider(BaseSceneScraper):
    name = 'IFeelMyself'
    network = 'Feck Erotica'
    parent = 'I Feel Myself'

    start_urls = ["https://ifeelmyself.com"]

    selector_map = {
        'external_id': r'media_id=([0-9]+)&',
        'description': '//td[@class="blog_wide_new_text"]/text()',
        'date': '//span[@class="entryDatestamp"]//text()',
        'date_formats': ['%d %b %Y'],
        'image': '//img/@src',
        'pagination': '/public/main.php?page=view&mode=all&offset=%s',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % ((page - 1) * 12))

    def get_scenes(self, response):
        for scene in response.xpath('//table[@class="ThumbTab ppss-scene"]/tr/td/a/@href').getall():
            split = scene.split("'")
            scene_id = split[1]
            artist_id = split[3]

            yield scrapy.Request(
                url="https://ifeelmyself.com/public/main.php?page=flash_player&out=bkg&media_id=" + scene_id + "&artist_id=" + artist_id,
                callback=self.parse_scene, meta={'site': 'I Feel Myself'})

    def get_title(self, response):
        title = response.xpath('//span[@class="entryHeadingFlash"]//a[1]/text()').get().replace("_", " ")
        title = string.capwords(title.strip())
        return title

    def get_performers(self, response):
        return [response.xpath('//span[@class="entryHeadingFlash"]/a[2]/text()').get().replace("_", " ")]

    def get_tags(self, response):
        tags = response.xpath('//table[@class="news_bottom_line"]/tr//text()').getall()
        tags = [t.strip() for t in tags]
        tags = [t.replace(";", "") for t in tags if t != '']
        enhanced_tags = response.xpath('//table[@class="news_tag_line"]//td/div/span/span[1]/text()').getall()
        fulltags = tags + enhanced_tags
        if "HD" in fulltags:
            fulltags.remove('HD')
        fulltags = list(map(lambda x: x.strip().title(), fulltags))
        return fulltags

    def get_all_performers(self, response):
        '''Override performers with correct value
            ifeelmyself displays videos with multiple performers as multiple videos, one under each name.
            We search for other copies of the video.
        '''
        # Rebuild object
        scene = SceneItem()
        for key in response.meta["scene"]:
            scene[key] = response.meta["scene"][key]

        # Override performers with search results (if other performers found)
        performers = response.xpath("//a[contains(@href,'artist')]/text()").getall()
        performers = [p.replace("_", " ") for p in performers]
        if performers != []:
            scene["performers"] = performers
        yield scene

    def parse_scene(self, response):
        for item in super().parse_scene(response):
            keywords = item["title"].replace(" ", "+")
            yield scrapy.FormRequest(
                url="https://ifeelmyself.com/public/main.php?page=search_results",
                meta={"scene": item},
                cookies={"ifm_search_keyword": keywords},
                formdata={"keyword": keywords},
                callback=self.get_all_performers)
