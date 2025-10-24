import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteStasyQSpider(BaseSceneScraper):
    name = 'StasyQ'
    network = 'StasyQ'
    parent = 'StasyQ'
    site = 'StasyQ'

    start_urls = [
        'https://www.stasyq.com',
    ]

    cookies = [{"domain":"www.stasyq.com","expirationDate":1747745117.127582,"hostOnly":true,"httpOnly":false,"name":"XSRF-TOKEN","path":"/","sameSite":"lax","secure":false,"session":false,"storeId":"0","value":"eyJpdiI6ImFqWnJzUDVtZWwvdWR2SGVmZ3hManc9PSIsInZhbHVlIjoiZ3BTQ2h1Z01PQXI0SVc2NStCVlY0WUF4QWJJVGJFL080UWt3dHZjYVFEQkYzMmxIZTJoVW9jaG4rZTI3b2ZSK2ZkWVFuQmhsTkVKTUxOQXRPaG5hbkFOTWVRMXRtWjNuUFlOQ044ZUZjVU1HRXlXcjBDNmpnSVVhdEtweXVxNzMiLCJtYWMiOiI3ODM1OTJiNTg4MzM1MTMwY2M4ZjlkYmFhZTAzZmNhNDUxNTRkZDM2MDg5Y2NmNTljMTdmMmZmOTk2OGU4YmY0IiwidGFnIjoiIn0%3D"},{"domain":"www.stasyq.com","expirationDate":1747745117.127656,"hostOnly":true,"httpOnly":true,"name":"stasyq_session","path":"/","sameSite":"lax","secure":false,"session":false,"storeId":"0","value":"eyJpdiI6IlhPd1JRM3A0N1MrUTJ2ZDFDcVMvaFE9PSIsInZhbHVlIjoiVFEwdWdjWUdNYkRyVDBmWnlrRU1QSTcvT3Q0dFM4THBOSUJGWldORlh0YWltRzVoSUtkeGdCSlpQeCtwdW5mVXo4UGNiOHpOM0syM0lFZWVXd2J0Qnh2eTdiVUVUMkpPK2NUNlp5VG9rVmNWSjRNNTRUNVlrUGdLdkhSNENGZCsiLCJtYWMiOiI2ZTkyNTliODQ2MGZlZmMxOGFiZDMyMmI2ZjI5ZjI1OGIzYzE4YTQxZDBlZjcyNzJlMGMzNjU4YTNkY2VjMGI2IiwidGFnIjoiIn0%3D"},{"domain":"www.stasyq.com","expirationDate":1776689117.12768,"hostOnly":true,"httpOnly":true,"name":"locale","path":"/","sameSite":"lax","secure":false,"session":false,"storeId":"0","value":"eyJpdiI6IjFHeWJqd2g2UXVYYmg5VERaWmRCUlE9PSIsInZhbHVlIjoiSVorYnhjT21sckVlOEJ5bWtRTnZ3RTRoYUVGNWVNdFh0U3pFaXFwT2xFZ2E3V042cEZaY2pBN0x1YlkyK3JLSSIsIm1hYyI6ImMwY2FmM2Q2Y2RjNWMzYjk3ZjZjNDFhYzBiNzRiYjA4ZjVhYWRiMTZiZGEwZjA4MzJmNGM2YzUyZDdjZjg3YzgiLCJ0YWciOiIifQ%3D%3D"},{"domain":".stasyq.com","expirationDate":1779713117.628892,"hostOnly":false,"httpOnly":false,"name":"_ga_J7XVT2Q94C","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"GS1.1.1745153117.1.0.1745153117.60.0.0"},{"domain":".stasyq.com","expirationDate":1779713117.629144,"hostOnly":false,"httpOnly":false,"name":"_ga","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"GA1.1.533472626.1745153118"}]

    selector_map = {
        'title': '//meta[@itemprop="position" and @content="2"]/preceding-sibling::a[1]/span/text()',
        'description': '//div[contains(@class, "about-section")]/p//text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="release-card__model"]/p/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'(\d+)$',
        'pagination': '/releases?sort=recent&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2[contains(text(), "All Releases")]//ancestor::section[1]//div[contains(@class,"release-preview-card__content")]|//h2[contains(text(), "The newest releases")]//ancestor::section[1]//div[contains(@class,"release-preview-card__content")]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[contains(@class, "d-flex")]/div[contains(@class, "text-grey")][1]/p/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                if scenedate:
                    meta['date'] = scenedate.group(1)

            scene = scene.xpath('.//h3/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Erotica']
