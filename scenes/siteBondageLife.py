import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteBondageLifeSpider(BaseSceneScraper):
    name = 'BondageLife'

    start_urls = [
        'https://www.bondagelife.com',
    ]

    cookies = [{"domain":".houseofgord.com","expirationDate":1763819185.391213,"hostOnly":false,"httpOnly":false,"name":"legal_accepted2","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"yes"},{"domain":".houseofgord.com","expirationDate":1757026557.214118,"hostOnly":false,"httpOnly":true,"name":"_hofg_session_v3","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"149ae63c574d840b770dd3b9e56d5598"}]

    selector_map = {
        'external_id': r'',
        'pagination': '/updates?page=%s',  # Last one now is 236
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//section[@class="nopadding"]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//p/b/text()[contains(., "/")]')
            if title:
                title = title.get()

                scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', title)
                if scenedate:
                    scenedate = scenedate.group(1)
                    item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

                title = re.search(r'(.*) - ', title)
                if title:
                    title = title.group(1)
                    item['title'] = string.capwords(self.cleanup_title(title.strip()))

                performers = scene.xpath('.//p/b/text()[not(contains(., "/"))]')
                if performers:
                    performers = performers.get()
                    performers = performers.lower().replace("starring", "").strip()
                    item['performers'] = [performers]

                description = scene.xpath('.//h5/text()')
                if description:
                    item['description'] = self.cleanup_description(description.get().strip())

                image = scene.xpath('.//h5/preceding-sibling::img/@src')
                if image:
                    image = self.format_link(response, image.get())
                    item['image'] = image
                    item['image_blob'] = self.get_image_blob_from_link(image)

                    item['id'] = re.search(r'posts/(.*?)/', image).group(1)

                    item['url'] = f"https://www.bondagelife.com/posts/{item['id']}"

                item['tags'] = ['Bondage']

                item['site'] = "BondageLife"
                item['parent'] = "BondageLife"
                item['network'] = "BondageLife"

            if item['id']:
                yield item
