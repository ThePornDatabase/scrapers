import re
import string
from PIL import Image
import base64
from io import BytesIO
import requests
import html
from slugify import slugify
import unidecode
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class SiteMyDirtyHobbySpecificPerformerSpider(BaseSceneScraper):
    name = 'MyDirtyHobbySpecificPerformer'
    network = 'MyDirtyHobby'
    parent = 'MyDirtyHobby'
    site = 'MyDirtyHobby'

    start_url = 'https://www.mydirtyhobby.com'

    cookies = [{"domain":"www.mydirtyhobby.com","hostOnly":true,"httpOnly":false,"name":"__s","path":"/profil","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"66B8EFDC-42FE728201BBC3CF4-2325A4"},{"domain":"www.mydirtyhobby.com","expirationDate":1744306131.472444,"hostOnly":true,"httpOnly":false,"name":"__l","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"66167A96-42FE728201BB3790AC-1A918"},{"domain":"www.mydirtyhobby.com","hostOnly":true,"httpOnly":false,"name":"PHPSESSID","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"ts7n1n91lqo5udsm2vilfhj5an"},{"domain":"www.mydirtyhobby.com","hostOnly":true,"httpOnly":false,"name":"LBSERVERID","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"ded7256"},{"domain":".mydirtyhobby.com","expirationDate":1725988731,"hostOnly":false,"httpOnly":false,"name":"ats","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"eyJhIjo5NDk2LCJjIjo0NTgxMzMyNSwibiI6MjEsInMiOjI0MSwiZSI6ODUzLCJwIjozfQ=="},{"domain":".mydirtyhobby.com","expirationDate":1723482460,"hostOnly":false,"httpOnly":false,"name":"atsd","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"6e172895-532b-495a-afc4-f500661448e0"},{"domain":".mydirtyhobby.com","expirationDate":1723396960,"hostOnly":false,"httpOnly":false,"name":"atsm","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"6e172895-532b-495a-afc4-f500661448e0"},{"domain":".mydirtyhobby.com","hostOnly":false,"httpOnly":false,"name":"atss","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"6e172895-532b-495a-afc4-f500661448e0"},{"domain":"www.mydirtyhobby.com","hostOnly":true,"httpOnly":false,"name":"__s","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"66B8EFDC-42FE728201BBC3CF4-2325AC"},{"domain":".mydirtyhobby.com","hostOnly":false,"httpOnly":false,"name":"etaguid","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"ecd819e3-006d-491f-8ced-26b60144d651"},{"domain":".mydirtyhobby.com","expirationDate":1754932063.298792,"hostOnly":false,"httpOnly":false,"name":"AGEGATEPASSED","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"1"},{"domain":".mydirtyhobby.com","hostOnly":false,"httpOnly":true,"name":"MDHSID","path":"/","sameSite":"unspecified","secure":true,"session":true,"storeId":"0","value":"5n2fdlo5bp75u4v9hibe08da7a"},{"domain":".mydirtyhobby.com","expirationDate":1723418331.163237,"hostOnly":false,"httpOnly":true,"name":"MDH","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"%21eyJvX2dlbmRlciI6IkEiLCJpc0xvZ2dlZCI6Im4iLCJscGFnZWlkIjo2LCJra0lEIjo0ODgzNiwibGFuZyI6InVzIiwibGFuZCI6ImRlIn0%3D%24018504784dd5589deece074beea2c5e47ff3a170"},{"domain":"www.mydirtyhobby.com","expirationDate":1754932644,"hostOnly":true,"httpOnly":false,"name":"COOKIE_CONSENT","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"000"},{"domain":".mydirtyhobby.com","expirationDate":1757956731.085989,"hostOnly":false,"httpOnly":false,"name":"atstrackPiece1","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"eyJhZmZVcmwiOiJjYXNoNG1lbWJlci5jb20iLCJhZmZDb2RlIjoiZXlKaElqbzVORGsyTENKaklqbzBOVGd4TXpNeU5Td2liaUk2TWpFc0luTWlPakkwTVN3aVpTSTZPRFV6TENKd0lqb3pmUT09IiwibmV0d29ya0NvZGUiOiJtZGgiLCJVSUQiOiI4NDA1NjU4My04ZjRmLTQ2MGItOTU3Ny1kOWY1OTY5MzliM2QiLCJTVUlEIjoiNmUxNzI4OTUtNTMyYi00OTVhLWFmYzQtZjUwMDY2MTQ0OGUwIiwiZGF0YSI6eyJ2YWx1ZSI6MSwiYWIiOjAsInVzZXJBZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMjcuMC4wLjAgU2FmYXJpLzUzNy4zNiBFZGcvMTI3LjAuMC4wIiwiYWRJZCI6MCwicmVmZXJyYWxEb21haW4iOiJodHRwOi8vb3JnYW5pYy8iLCJyZWZlcnJhbFBhdGgiOiJodHRwOi8vb3JnYW5pYy8iLCJ2b3J0ZXhHdWlkIjoiZWNkODE5ZTMtMDA2ZC00OTFmLThjZWQtMjZiNjAxNDRkNjUxIn0sImRtcCI6e30sImRlZmF1bHRDb2RlIjoiZXlKaElqbzVORGsyTENKaklqbzBORFEzTXpNMk5Dd2liaUk2TWpFc0luTWlPakkwTVN3aVpTSTZPRFV6TENKd0lqb3pmUT09Iiwic3BsaXRBdGxhc0RhdGEiOnRydWUsImRpc2FibGUiOmZhbHNlLCJzdGVwcyI6Inw7ZDt2O3Q7dTt8O2FjO3Y7dDt8O2FjO3Y7dDt8O2FjO3Y7dDt8Iiwidm9ydGV4ZGF0YSI6eyJfc3NjcmVlbiI6IjE5MjAgeCAxMDgwIiwiX3Nicm93"},{"domain":".mydirtyhobby.com","expirationDate":1757956731.086051,"hostOnly":false,"httpOnly":false,"name":"atstrackPiece2","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"c2VyIjoiQ2hyb21lIiwiX3Nicm93c2VyVmVyc2lvbiI6IjEyMy4wLjAuMCIsIl9ibW9iaWxlIjpmYWxzZSwiX3NvcyI6IldpbmRvd3MgTlQgNC4wIiwiX3Nvc1ZlcnNpb24iOiJOVCA0LjAiLCJfc2ZsYXNoVmVyc2lvbiI6Im5vIGNoZWNrIiwiX3NsYW5ndWFnZXMiOiJlbi1VUyxlbiIsImd1aWQiOiJlY2Q4MTllMy0wMDZkLTQ5MWYtOGNlZC0yNmI2MDE0NGQ2NTEiLCJod21vZGVsIjoiVW5rbm93biIsImh3ZmFtaWx5IjoiRW11bGF0b3IiLCJkZXZ0eXBlIjoiRGVza3RvcCJ9LCJ2aXNpdFN0YXJ0IjoxNzIzMzk2MDYwNDU0LCJjb2RlVHlwZSI6ImF0cyJ9"}]

    paginations = [
        {"site": "My Dirty Hobby: Lara Cumkitten", "profile": "5160121-Lara-CumKitten", "performer": "Lara Cumkitten", "date_format": "%d/%m/%y"},
        {"site": "My Dirty Hobby: Baebaezoe", "profile": "129036471-baebaezoe", "performer": "Baebaezoe", "date_format": "%d/%m/%y"},
        {"site": "My Dirty Hobby: AliceKinkycat", "profile": "9919941-AliceKinkycat", "performer": "Alice Kinkycat", "date_format": "%d/%m/%y"},
        {"site": "My Dirty Hobby: Dirty Tina", "profile": "2517040-Dirty-Tina", "performer": "Dirty Tina", "date_format": "%d/%m/%y"},
        {"site": "My Dirty Hobby: CandyXS", "profile": "77262612-CandyXS", "performer": "Candy XS", "date_format": "%d/%m/%y"},
        {"site": "My Dirty Hobby: Young Devotion", "profile": "9996261-Young-Devotion", "performer": "Chloe", "date_format": "%d/%m/%y"},
        {"site": "My Dirty Hobby: Fickfreundinnen", "profile": "50381232-Fickfreundinnen", "performer": "Ramona", "date_format": "%d/%m/%y"},
        {"site": "My Dirty Hobby: Schnuggie91", "profile": "4544623-schnuggie91", "performer": "Sophie", "date_format": "%d/%m/%y"},
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/content/api/videos',
        'type': 'Scene',
    }

    def get_next_page_url(self, page, profile):
        profile_id = re.search(r'(\d+)', profile).group(1)
        link = f"https://www.mydirtyhobby.com/content/api/v2/videos?page={str(page)}&pagesize=20&user_language=en&user_id={profile_id}"
        return link

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        link = "https://www.mydirtyhobby.com/"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        for pagination in self.paginations:
            meta['site'] = pagination['site']
            meta['profile'] = pagination['profile']
            meta['performers'] = [pagination['performer']]
            meta['date_format'] = pagination['date_format']
            yield scrapy.Request(url=self.get_next_page_url(self.page, meta['profile']), method='POST', callback=self.parse, meta=meta, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def parse(self, response, **kwargs):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        print(f"Count: {count}   Page: {meta['page']}")
        if count:
            if meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta['profile']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        if jsondata:
            jsondata = jsondata['items']
            for scene in jsondata:
                item = self.init_scene()
                item['title'] = unidecode.unidecode(html.unescape(string.capwords(scene['title']).strip()))
                item['description'] = unidecode.unidecode(html.unescape(string.capwords(scene['description']).strip()))
                item['performers'] = meta['performers']
                item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['latestPictureChange']).group(1)
                item['url'] = f"https://www.mydirtyhobby.com/profil/{meta['profile']}/videos/{scene['uv_id']}-{slugify(item['title'])}"
                item['id'] = scene['uv_id']
                item['site'] = meta['site']
                item['duration'] = self.duration_to_seconds(scene['duration'])
                item['parent'] = "MyDirtyHobby"
                item['network'] = "MyDirtyHobby"
                item['trailer'] = ''
                item['image'] = scene['thumbnail']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
                item['tags'] = []

                yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image and self.cookies:
            cookies = {cookie['name']:cookie['value'] for cookie in self.cookies}
            req = requests.get(image, cookies=cookies, verify=False)
            # ~ req = Http.get(image, headers=response.headers, cookies=self.cookies, verify=False)

            if req and req.ok:
                return req.content
        return None

    def get_image_blob_from_link(self, image):
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        if (not force_update or (force_update and "image" in force_fields)) and image:
            data = self.get_image_from_link(image)
            if data:
                try:
                    img = BytesIO(data)
                    img = Image.open(img)
                    img = img.convert('RGB')
                    width, height = img.size
                    if height > 1080 or width > 1920:
                        img.thumbnail((1920, 1080))
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    data = buffer.getvalue()
                except Exception as ex:
                    print(f"Could not decode image for evaluation: '{image}'.  Error: ", ex)
                return base64.b64encode(data).decode('utf-8')
        return None
