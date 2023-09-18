import re
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
        'date': '//div[@class="blog-title-right"]/text()',
        'date_formats': ['%d %b %Y'],
        'image': '//img/@src',
        'pagination': '/public/main.php?page=view&mode=all&offset=%s',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % ((page - 1) * 12))

    def get_scenes(self, response):
        for scene in response.xpath('//table[@class="DispResults"]'):
            if scene.xpath('.//a[contains(@href, "photoshoot")]'):
                print("Scene is a Photoshoot, not Video")
            else:
                imagealt = scene.xpath('.//img/@src').get()
                datealt = scene.xpath('.//td[@align="right"]/text()')
                passdate = ''
                if datealt:
                    datealt = datealt.get()
                    datealt = re.search(r'(\d{1,2} \w+ \d{4})', datealt)
                    if datealt:
                        datealt = datealt.group(1)
                        passdate = self.parse_date(datealt, ['%d %b %Y']).isoformat()
                scenelink = scene.xpath('.//a[contains(@href, "javascript")]').get()
                try:
                    split = scenelink.split("'")
                except:
                    errortext = scene.xpath('.//b/a[contains(@href, "public")]/../..//text()').getall()
                    errortext = " ".join(errortext).replace("\n", " ").replace("  ", " ")
                    print(f"Error on parsing: {errortext}")
                scene_id = split[1]
                artist_id = split[3]

                yield scrapy.Request(
                    url="https://ifeelmyself.com/public/main.php?page=flash_player&out=bkg&media_id=" + scene_id + "&artist_id=" + artist_id,
                    callback=self.parse_scene, meta={'site': 'I Feel Myself', 'imagealt': imagealt, 'datealt': passdate})

    def get_title(self, response):
        title = response.xpath('//span[@class="entryHeadingFlash"]//a[1]/text()').get().replace("_", " ")
        title = string.capwords(title.strip())
        return title

    def get_performers(self, response):
        return [response.xpath('//span[@class="entryHeadingFlash"]/a[2]/text()').get().replace("_", " ")]

    def get_tags(self, response):
        tags = response.xpath('//table[@class="news_bottom_line"]/tr//text()').getall()
        enhanced_tags = response.xpath('//table[@class="news_tag_line"]//td/div/span/span[1]/text()').getall()
        fulltags = tags + enhanced_tags
        if "HD" in fulltags:
            fulltags.remove('HD')
        fulltags = list(map(lambda x: x.strip().title(), fulltags))
        fulltags2 = []
        for t in fulltags:
            t = t.replace(";", "")
            t = t.replace("\\r", "")
            t = t.replace("\\n", "")
            t = t.replace("\\t", "")
            t = t.replace("Explicit Content Solo", "")
            t = t.strip()
            if t:
                fulltags2.append(t)
        return fulltags2

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
        meta = response.meta
        for item in super().parse_scene(response):
            keywords = item["title"].replace(" ", "+")
            if "tags.png" in item['image']:
                item['image'] = meta['imagealt']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if not item['date'] and meta['datealt']:
                item['date'] = meta['datealt']
            yield scrapy.FormRequest(
                url="https://ifeelmyself.com/public/main.php?page=search_results",
                meta={"scene": item},
                cookies={"ifm_search_keyword": keywords},
                formdata={"keyword": keywords},
                callback=self.get_all_performers)
