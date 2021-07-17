import re
import csv
import scrapy
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

class LustCinemaSpider(BaseSceneScraper):
    name = 'LustCinema'

    start_urls = ["https://lustcinema.com"]

    selector_map = {
        'title': '//h2/text()',
        'external_id': 'movies/(.+)',
        'image': '//img/@src',
        'performers': '//a[contains(@href,"/cast/")]/text()',
        'pagination': '/categories/lust-cinema-originals',
        'pagination': '/movies',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination'))

    def get_scenes(self, response):
        for scene in response.xpath('//a[contains(@href, "/movies/")]/@href').getall():
            yield scrapy.Request(
                url=self.format_url(self.start_urls[0], scene),
                callback=self.parse_scene)

    def get_image(self, response):
        metadata = self.get_metadata(response)
        url = metadata["poster_picture"]
        if url == "null":
            url = metadata["cover_title_picture"]
        return bytes(url, "ascii").decode('unicode-escape')

    def get_description(self, response):
        metadata = self.get_metadata(response)
        description = bytes(metadata["synopsis"], "utf-8").decode("unicode-escape")
        description = re.sub('<[^<]+?>', '', description).strip()
        return description

    def get_metadata(self, response):
        '''Gets the scene metadata hidden in script tag'''
        for script in response.xpath("//script/text()").getall():
            if "NUXT" in script:
                split = script.split(";")
                data = script.split("}(")[1]
                order = split[0].split("function(")[1].split(")")[0].split(",")

                # key mapping
                mapping = {}
                for s in split:
                    sSplit = s.split("=")
                    if len(sSplit) == 2:
                        if "{" in sSplit[1]:
                            # Nested
                            sub = sSplit[1].replace("{", "")
                            sub = sub.split("},")
                            out = []
                            for sList in sub:
                                sListOut = {}
                                for s in sList.split(","):
                                    sSplit2 = s.split(":")
                                    sListOut[sSplit2[0]] = sSplit2[1].replace("}", "")
                                out.append(sListOut)

                            mapping[sSplit[0]] = out
                        else:
                            mapping[sSplit[0]] = sSplit[1]

                # values
                dSplit = ['{}'.format(x) for x in list(csv.reader([data], delimiter=',', quotechar='"'))[0] ]
                for key in mapping:
                    if "{" in mapping[key]:
                        mSplit = mapping[key].split(",")
                        mSplit = [m.replace("{", "").replace("}", "") for m in mSplit]
                        mapping[key] = {}
                        for m in mSplit:
                            mapping[key][m.split(":")[0]] = m.split(":")[1]

                if response.xpath("//h2/text()").get().strip() == "Girl Friday":
                    breakpoint()
                # Construct object
                output = {}
                for key in mapping:
                    formatted_key = key.split(".")[-1]
                    if isinstance(mapping[key], str):
                        try:
                            output[formatted_key] = dSplit[order.index(mapping[key])]
                        except:
                            pass
                    else:
                        output[formatted_key] = []
                        for mapp in mapping[key]:
                            subOutput = {}
                            for subkey in mapp:
                                try:
                                    subOutput[subkey.replace("[", "")] = dSplit[order.index(mapp[subkey])]
                                except:
                                    pass
                            output[formatted_key].append(subOutput)
                return output

    def get_tags(self, response):
        metadata = self.get_metadata(response)
        tags = [t["title"] for t in metadata["tags"] if "Discover" not in t["title"]]

        # Remove non-tags
        for t in ["Lust Cinema Originals", "Top 10 Movies of the Month", "Wicked"]:
            try:
                tags.remove(t)
            except ValueError:
                pass
        return tags

    def get_parent(self, response):
        metadata = self.get_metadata(response)
        tags = [t["title"] for t in metadata["tags"] if "Discover" in t["title"] or "Wicked" in t["title"]]
        if len(tags) == 0:
            return "Lust Cinema"
        else:
            if tags[0] == "Wicked":
                return "Wicked"
            return " ".join(tags[0].split()[1:])

    def get_network(self, response):
        return self.get_parent(response)

    def get_date(self, response):
        metadata = self.get_metadata(response)
        return dateparser.parse(metadata["release_date"]).isoformat()

    def get_performers(self, response):
        performers = response.xpath(self.selector_map["performers"]).getall()
        return [bytes(p, "utf-8").decode("unicode-escape").strip() for p in performers]


