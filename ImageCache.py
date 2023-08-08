import glob
import Utils
from datetime import datetime, timedelta
from pathlib import Path

import pywikibot
from PIL import Image

def get_json_sprites(items):
    sprites = set()
    for item in items:
        sprites.add(item)
        return list(sprites)


class ImageManager:

    def __init__(self, site):
        self.image_cache_file = Path('./image_cache.txt')
        self.site = site
        self.images = dict()
        self.sprites_directory = './sprites/'
        self.read_cache_file()

    def get_local_image_name(self, item_name):

        search_str = Path(self.sprites_directory + '/' + item_name + '_*.png')

        l = glob.glob(str(search_str.absolute()))
        if len(l) == 1:
            return l[0]
        else:
            return None

    def normalize_names(self, item):
        if isinstance(item, dict):
            fname = Path(item['sprite'])
            image_location = fname.absolute()
            item_name = item['name']
        elif isinstance(item, str):
            image_location = self.get_local_image_name(item)
            item_name = item
        return image_location, item_name

    def get_sprite_size(self, item):
        image_location, item_name = self.normalize_names(item)
        image = Image.open(image_location)
        x, y = image.size
        return str(x) + 'x' + str(y) + 'px'

    def get_local_item_hash(self, item):
        image_location, item_name = self.normalize_names(item)
        tmp = Utils.compute_file_hash(image_location)
        return tmp

    def image_info(self, item):
        image_location, item_name = self.normalize_names(item)
        stored_hash, remote_hash, stored_time = self.images[item_name]
        yesterday = datetime.now() - timedelta(1)
        if stored_time < yesterday.timestamp():
            self.update_image(item)
        local_hash, remote_hash, stored_time = self.images[item_name]
        return stored_hash, remote_hash

    def add_image(self, item):
        if isinstance(item, list):
            for x in item:
                self.add_image(x)
        elif isinstance(item, dict):
            image_location, item_name = self.normalize_names(item)
            local_hash, remote_hash,time = self.images[item_name]
            self.images[item_name] = (self.get_local_item_hash(item),remote_hash,Utils.get_now_unix())


    def remove_image(self, image):
        self.images.pop(image)

    def update_image(self, item, delay_write=False):
        image_location, item_name = self.normalize_names(item)
        if item in self.images.keys():
            self.images[item] = (
                self.get_local_item_hash(item), self.get_remote_hash(item_name), Utils.get_now_unix())
        else:
            self.add_image(item)
        if not delay_write:
            self.write_cache_file()

    def write_cache_file(self):
        with open(str(self.image_cache_file), 'w') as file:
            for key, cache_value in self.images.items():
                local_hash, remote_hash, cache_time = cache_value
                file.write(str(key) + '=' + str(local_hash) + ',' + str(remote_hash) + ',' + str(cache_time) + '\n')
        return

    def read_cache_file(self):
        if not self.image_cache_file.exists():
            return
        with open(str(self.image_cache_file), 'r') as file:
            lines = file.readlines()
        for line in lines:
            key, cache_value = line.split('=')
            local_hash, remote_hash, cache_time = cache_value.split(',')
            self.images[key] = (str(local_hash), str(remote_hash), float(cache_time))

    def get_web_images_status(self):
        for idx, item in enumerate(self.images):
            if (idx + 1) % 100 == 0:
                self.write_cache_file()
                print(str(idx) + ' of ' + str(len(self.images)))
            self.update_image(item, delay_write=True)
        self.write_cache_file()

    def get_remote_hash(self, item):

        image_location, item_name = self.normalize_names(item)

        filepage = pywikibot.FilePage(self.site, item_name +'.png')
        if filepage.exists():
            try:
                return filepage.latest_file_info.sha1
            except:
                return None
        else:
            return None

    def upload_image(self, item, new_name=None, delay_write=False):

        image_location, item_name = self.normalize_names(item)
        if new_name == None:
            new_name = item_name + '.png'

        local_hash, remote_hash = self.image_info(item_name)
        if local_hash != remote_hash:
            filepage = pywikibot.FilePage(self.site, new_name)
            comment = new_name + ' image uploaded by a robot'
            text = ''
            image_string = str(image_location.absolute())

            filepage.upload(source=image_string, text=text, comment=comment, ignore_warnings=True,
                            report_success=False)
            filepage.save(summary=comment)

            self.update_image(item)
            if not delay_write:
                self.write_cache_file()

    def upload_new_images(self):
        for idx, item in enumerate(self.images.keys()):
            if (idx + 1) % 100 == 0:
                print(str(idx) + ' ' + str(len(self.images.keys())))
                self.write_cache_file()
            self.upload_image(item)
        self.write_cache_file()
