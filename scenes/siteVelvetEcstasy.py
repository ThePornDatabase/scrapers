import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteVelvetEcstasySpider(BaseSceneScraper):
    name = 'VelvetEcstasy'
    network = 'Velvet Ecstasy'
    parent = 'Velvet Ecstasy'
    site = 'Velvet Ecstasy'

    start_urls = [
        'https://www.velvetecstasy.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/visitors/tour%s.htm',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if page < 10:
            page = "0" + str(page)
        else:
            page = str(page)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.xpath('//table[@width="1200" and @cellpadding="5"]')
        for scene in scenes:
            if scene.xpath('.//*').getall():
                # ~ print()
                # ~ print()
                # ~ print(scene.xpath('.//*').getall())
                # ~ print()
                item = SceneItem()
                item['title'] = self.cleanup_title(scene.xpath('.//font[@size="5"]/b//text()|.//font[@size="5"]/strong//text()|.//b/font[@size="5"]//text()|.//b/font[@size="5"]//text()|.//font[@size="4"]//font[@size="5"]//text()').get())
                description = scene.xpath('.//td//font[@size="2"]/text()')
                item['description'] = ""
                if description:
                    description = "".join(description.getall())
                    description = description.replace("\\n", "").replace("\n", "")
                    description = " ".join(description.split())
                    item['description'] = self.cleanup_description(description)
                performers = scene.xpath('.//td/div//font[contains(text(), "Starring")]/following-sibling::font[1]//text()')
                item['performers'] = []
                if performers:
                    performers = performers.getall()
                    performers = " ".join(performers).strip()
                    if "&" in performers:
                        performers = performers.split("&")
                    item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
                scenedate = scene.xpath('./preceding-sibling::font[1]//text()')
                item['date'] = None
                if scenedate:
                    scenedate = scenedate.get()
                    scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate)
                    if scenedate:
                        scenedate = scenedate.group(1)
                        item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
                tags = scene.xpath('.//font/b[contains(text(), "Action:")]/following-sibling::text()')
                item['tags'] = []
                if tags:
                    tags = tags.get()
                    tags = tags.split(",")
                    item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
                origimage = self.format_link(response, scene.xpath('.//img/@src').get())
                item['image'] = origimage.replace(".com/", ".com/visitors/").replace("_thumb", "_photo").replace("/thumbs/", "/photos/")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                if not item['image_blob']:
                    item['image'] = origimage.replace(".com/", ".com/visitors/")
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                duration = scene.xpath('.//font[contains(text(), "minutes")]//text()')
                if duration:
                    duration = " ".join(duration.getall())
                    duration = re.search(r'(\d+) [mM]inute', duration)
                    if duration:
                        item['duration'] = str(int(duration.group(1)) * 60)

                item['url'] = self.format_link(response, scene.xpath('.//a/@href').get()).replace(".com/", ".com/visitors/")
                if "scenes.htm" in item['url'] and item['image']:
                    item['id'] = re.search(r'.*/(.*?)_photo', item['image'])
                    if item['id']:
                        item['id'] = item['id'].group(1)
                    else:
                        item['id'] = re.search(r'.*/(.*?)_thumb', item['image']).group(1)
                else:
                    item['id'] = re.search(r'.*/(.*?)\.htm', item['url']).group(1)
                item['site'] = "Velvet Ecstasy"
                item['parent'] = "Velvet Ecstasy"
                item['network'] = "Velvet Ecstasy"
                item['trailer'] = None
                yield self.check_item(item, self.days)
