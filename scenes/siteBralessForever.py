import re
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

class SiteBralessForeverSpider(BaseSceneScraper):
    name = 'BralessForever'

    start_urls = [
        'https://app.bralessforever.com',
    ]

    selector_map = {
        'external_id': r'videos/(.*)',
        'pagination': '/browse/videos?channel_visibility=%%22ALL%%22&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        parsed_data = self.parse_flight_data(response.text)

        parser = SiteBralessFlightResolver(parsed_data)
        video_objects = self.find_videos_recursive(parser.get_full_object())
        scenes = []

        for video in video_objects:
            scenes.append(f"/videos/{video.get('id')}")

        meta = response.meta

        # testing videos:
        # scenes = [
            # "/videos/153baf2a-f194-46b2-bef6-f7ecf0b285c5",
            # "/videos/dbb48172-6950-4aee-8e12-dd8cbe552000",
            # "/videos/7bde84f1-59f1-4cca-b40a-7aae29cc896e",
            # "/videos/33e40cc0-c9e5-445a-b718-201a747d204a"
        # ]

        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        parsed_data = self.parse_flight_data(response.text)
        parser = SiteBralessFlightResolver(parsed_data)
        full_data = parser.get_full_object()
        jsondata = self.find_video_recursive(full_data)

        # To check what data the object has
        # if jsondata:
        #     json.dump(jsondata, open("media.json", "a"), indent=2)

        # item = SceneItem() # for some reason, the type of performers_data don't match with the SceneItem()
        item = {}


        item['title'] = self.cleanup_title(jsondata['name'])
        if "display_date" in jsondata and jsondata['display_date']:
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', jsondata['display_date']).group(1)

        item['description'] = ''
        if "description" in jsondata and jsondata['description']:
            desc = self.cleanup_description(jsondata['description'])
            item['description'] = " ".join(desc.split())

        image = self.get_best_image(jsondata)
        item['image'] = ''
        item['image_blob'] = ''
        if image:
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(image)

        item['url'] = response.url
        item['id'] = re.search(r'videos/(.*)', response.url).group(1)

        item['duration'] = None
        if "duration" in jsondata and jsondata['duration']:
            item['duration'] = jsondata['duration']

        item['performers'] = []
        item['performers_data'] = []
        actors = jsondata.get('contentUserCredits', [])

        if actors and isinstance(actors, list):
            # Loop through each credit and extract the name safely
            for actor in actors:
                user = actor.get('contentUser')
                if user and user.get('effectiveName'):
                    item['performers'].append(string.capwords(user['effectiveName']))
                    item['performers_data'].append(self.get_performer_data(user))


        item['site'] = "Braless Forever"
        item['parent'] = "Braless Forever"
        item['network'] = "Braless Forever"
        item['trailer'] = jsondata.get('effectivePreviewVideoUrl', '')
        item['tags'] = []

        # not by default in the SceneItem object, but might be useful
        item['categories'] = []
        categories_list = jsondata.get('categories', [])
        if categories_list:
            item['categories'] = [cat['name'] for cat in categories_list if 'name' in cat]

        yield self.check_item(item, self.days)

    def get_performer_data(self, contentUser):
        perf = {}
        perf['name'] = string.capwords(contentUser.get('effectiveName'))
        perf['extra'] = {}
        perf['extra']['gender'] = "Female"
        perf['network'] = "Braless Forever"
        perf['site'] = "Braless Forever"
        # user = contentUser.get('user') or {}
        avatar = contentUser.get('avatar') or {}
        image_data = avatar.get('data') or {}
        blob = image_data.get('o')

        if blob:
            perf['image'] = blob
            perf['image_blob'] = self.get_image_blob_from_link(blob)

        return perf


    def parse_flight_data(self, html):
        push_pattern = r'__next_f\.push\(\[\s*\d+\s*,\s*"((?:\\.|[^"\\])*)"\s*\]\s*\)'
        chunks = re.findall(push_pattern, html)
        flight = "".join(json.loads(f"\"{c}\"") for c in chunks)
        return flight

    def find_videos_recursive(self, data, found_videos=None):
        """
        Recursively searches for ALL keys named 'video' that contain 'id' and 'name'.
        """
        if found_videos is None:
            found_videos = []

        if isinstance(data, dict):
            # 1. Check current level
            if 'video' in data and isinstance(data['video'], dict):
                video_node = data['video']
                if 'id' in video_node and 'name' in video_node:
                    found_videos.append(video_node)

            # 2. Continue searching deeper in all keys
            for value in data.values():
                self.find_videos_recursive(value, found_videos)

        elif isinstance(data, list):
            # 3. Continue searching deeper in all list items
            for item in data:
                self.find_videos_recursive(item, found_videos)

        return found_videos

    def find_video_recursive(self, data):
        """
        Recursively searches for a key named 'video' that contains 'id' and 'name'.
        """
        return self.find_videos_recursive(data)[0] or None

    def get_best_image(self, video):
        effectiveCover = video.get('effectiveCover', {})

        if not effectiveCover:
            return None

        variants = effectiveCover.get('variants', [])

        if not variants:
            return None

        # Find the variant with the maximum width
        best_variant = max(variants, key=lambda x: x.get('width', 0))
        return best_variant.get('url')


"""
Helper class to resolve Next.js Flight data references
"""
class SiteBralessFlightResolver:
    def __init__(self, raw_input):
        self.chunks = {}
        self._parse_data(raw_input)

    def _parse_data(self, data):
        """Processes the raw string block into the chunk map."""
        lines = data.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue

            # Find the first colon to split ID from content
            idx = line.find(':')
            chunk_id = line[:idx]
            content = line[idx+1:]

            # Handle different Next.js prefixes (I, HL, T)
            if content.startswith(('I', 'HL', 'T')):
                # Find where the JSON actually starts after the prefix
                json_start = content.find('[')
                if json_start == -1:
                    json_start = content.find('{')

                if json_start != -1:
                    try:
                        self.chunks[chunk_id] = json.loads(content[json_start:])
                    except json.JSONDecodeError:
                        self.chunks[chunk_id] = content
                else:
                    self.chunks[chunk_id] = content
            else:
                # Standard raw JSON data
                try:
                    self.chunks[chunk_id] = json.loads(content)
                except json.JSONDecodeError:
                    self.chunks[chunk_id] = content

    def _resolve(self, node):
        if isinstance(node, list):
            return [self._resolve(i) for i in node]

        if isinstance(node, dict):
            return {k: self._resolve(v) for k, v in node.items()}

        if isinstance(node, str):
            # 1. Regex: Handles $L13, $13, $c, $L61, etc.
            # It captures the "ID" part into group 2
            ref_match = re.match(r'^\$(?:L|W|I)?([a-fA-F0-9]+)$', node)
            if ref_match:
                ref_id = ref_match.group(1)

                # Check both string and potentially integer versions of the ID
                target = self.chunks.get(ref_id) or self.chunks.get(f"$L{ref_id}")

                if target is not None:
                    # If we found it, recurse to _resolve nested refs inside the new chunk
                    return self._resolve(target)

            # 2. Handle "Double Encoded" JSON strings inside the tree
            if (node.startswith('[') and node.endswith(']')) or (node.startswith('{') and node.endswith('}')):
                try:
                    return self._resolve(json.loads(node))
                except (json.JSONDecodeError, TypeError):
                    return node

            if node == "$undefined":
                return None

        return node

    def get_full_object(self):
        """Starts reconstruction from the root (ID 0)."""
        root = self.chunks.get('0')
        if root is None:
            # If 0 is missing, return the flat map for debugging
            return {"error": "Root chunk 0 not found", "available_ids": list(self.chunks.keys())}
        return self._resolve(root)

