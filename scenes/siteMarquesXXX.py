import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMarquesXXXSpider(BaseSceneScraper):
    name = 'MarquesXXX'

    start_urls = [
        'https://onnowplay.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/marquesxxx/videos/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-list-thumbs")]/div')
        for scene in scenes:
            item = self.init_scene()
            title = scene.xpath('.//h2/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())

            image = scene.xpath('.//video/@poster')
            if image:
                item['image'] = image.get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            
            url = scene.xpath('./a/@href')
            if url:
                item['url'] = url.get()
                item['site'] = 'MarquesXXX'
                item['network'] = 'MarquesXXX'
                item['parent'] = 'MarquesXXX'
                item['id'] = re.search(r'.*/(.*?)$', item['url']).group(1)

            duration = scene.xpath('.//i[@class="icon-time"]/following-sibling::text()')
            if duration:
                duration = duration.get().strip()
                item['duration'] = sum(int(v) * (60 if u == 'm' else 1) for v, u in re.findall(r'(\d+)([ms])', duration))

            yield item