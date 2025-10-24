import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class TonightsGirlfriendSpider(BaseSceneScraper):
    name = 'TonightsGirlfriend' # Moved into NaughtyAmerica API Scraper
    network = 'Tonights Girlfriend'
    parent = 'Tonights Girlfriend'

    start_urls = []

    cookies = [{"domain":".www.tonightsgirlfriend.com","expirationDate":1759344991,"hostOnly":false,"httpOnly":false,"name":"aws-waf-token","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"260dcd9b-9f10-4c42-8aeb-11bd469040e8:EQoAinWE76kqAAAA:OmTMrMiBSsUZ+lmchVk3RkMQq6Te7Bgi+hXZGiFNIJWz1Z0KxyHRGwYg1/ATeoDbA08WUZpwrSYpdtBM38fSXjPrkQP6o5wlGn7O87aVLyxLu5qPiWY1A0wTm8ZKcxJUcAPVedcN9DNfM8Uh5p3Tm+KnLiXH51RGrMG/JVowmfrTVWGmAzerwPKbVwBNzdEF5/EB20971+DK9muNk/RoS4IKOE5Vag=="},{"domain":"www.tonightsgirlfriend.com","expirationDate":1759006773.083248,"hostOnly":true,"httpOnly":true,"name":"naughty_session","path":"/","sameSite":"lax","secure":false,"session":false,"storeId":"0","value":"g4AXqy6xeg4bFXJdruF4Y81WNe0OEIGDRT7OT3bY"},{"domain":"www.tonightsgirlfriend.com","expirationDate":1759085792,"hostOnly":true,"httpOnly":false,"name":"preview_counter","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"3"},{"domain":"www.tonightsgirlfriend.com","expirationDate":1759604372.083045,"hostOnly":true,"httpOnly":false,"name":"AWSALB","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"rMSdbOiCZoJKz0pQY0Bvkik4dCBizVrTJKWazfPsw7jlnKFaG6H8oDilfFAS22UDkpkvG/AQ/XN1AE3AXPhL0U7s9f+UB+8S6WYm8O66lY9Kpxugcbs35Mp82uQP"},{"domain":"www.tonightsgirlfriend.com","expirationDate":1759604372.08319,"hostOnly":true,"httpOnly":false,"name":"AWSALBCORS","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"rMSdbOiCZoJKz0pQY0Bvkik4dCBizVrTJKWazfPsw7jlnKFaG6H8oDilfFAS22UDkpkvG/AQ/XN1AE3AXPhL0U7s9f+UB+8S6WYm8O66lY9Kpxugcbs35Mp82uQP"}]

    selector_map = {
        'description': "//p[contains(@class, 'scene-description')]/text()",
        'performers': "//p[contains(@class, 'performers')]/a/text()",
        'date': "//span[@class='scenepage-date']/text()",
        'image': "//img[@class='playcard']/@src",
        'tags': '//div[contains(@class, "category")]/a/text()',
        'external_id': r'scene/(.+)',
        'trailer': '',
        'pagination': r'/scenes?page=%s'
    }

    def get_title(self, response):
        title = response.xpath('//h1[contains(@class, "title")]/text()')
        if title:
            return self.cleanup_title(title.get())
        externid = self.get_id(response).replace('-', ' ')
        externid = re.sub(r"(\d+)$", "", externid)
        return externid.title()

    def get_scenes(self, response):
        scenes = response.css(
            'div.panel .scene-thumbnail a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
