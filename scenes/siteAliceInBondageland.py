import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAliceInBondagelandSpider(BaseSceneScraper):
    name = 'AliceInBondageland'
    network = 'Alice In Bondageland'
    parent = 'Alice In Bondageland'
    site = 'Alice In Bondageland'

    start_urls = [
        'http://www.aliceinbondageland.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/Updates-External/index.php?sel=%s&vids_only=1',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = (page - 1) * 20
        return self.format_url(base, self.get_selector_map('pagination') % page)
    
    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//p[span[contains(@class,"Verdana-VideoTitle-13pxBold")]]/ancestor::table[@width="100%"][1]')
        if len(scenes) < 2:
            print(f"Less than 2 scenes found, stopping pagination.  {response.url}")
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//span[contains(@class,"VideoTitle")]/following-sibling::span//a/text()')
            if title:
                item['title'] = string.capwords(self.cleanup_title(title.get()).strip())
            
            descripton = scene.xpath('.//td[@colspan="3"]/span[contains(@class,"Verdana-White12px")]//text()')
            if descripton:
                item['description'] = self.cleanup_description(" ".join(descripton.getall()).strip())

            scenedate = scene.xpath('.//p[contains(@class,"Varanda10Pt-White")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = scenedate.replace("\r", "").replace("\n", "").replace("\t", "").strip()
                scenedate = re.search(r'(\d{1,2} \w+, \d{1,4})', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                    item['date'] = self.parse_date(scenedate, date_formats=['%d %b, %y']).strftime('%Y-%m-%d')

            image = scene.xpath('.//td[@width="50%" and @align="center"]//img/@src')
            if image:
                image = self.format_link(response, image.get()).replace("../", "")
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)_\d+\.', image).group(1).lower()

            item['site'] = "Alice in Bondageland"
            item['network'] = "Alice in Bondageland"
            item['parent'] = "Alice in Bondageland"

            item['url'] = f"http://www.aliceinbondageland.com/videos/{item['id']}/"

            if item['id'] and self.check_item(item, self.days):
                yield item
            