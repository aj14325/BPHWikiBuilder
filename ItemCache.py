import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import pywikibot
import threading
import Utils

json_fields = ['name', 'sprite', 'shape', 'validChar', 'rarity', 'types', 'useCost', 'special', 'descriptions',
               'version', 'summonCost']
wikitext_fancy_template = 'Itemcard \n|item name= {name} \n|use cost= {use_cost} \n|extra icons= {icons} \n|item shape= {shape} \n|shape size= {shape_size} \n|sprite size= {sprite_size} \n|type= {type} \n|rarity= {rarity} \n|rarity color= {rarity_color} \n|stats= {stats} \n'
wikitext_passive_template = 'PassiveItemcard\n|item name={name}\n|extra icons={icons}\n|item shape={shape}\n|shape size={shape_size}\n|sprite size={sprite_size}\n|type={type}\n|rarity={rarity}\n|rarity color={rarity_color}\n|stats={stats}\n'
wikitext_fancy_fields = ['name', 'use_cost', 'icons', 'shape', 'shape_size', 'sprite', 'sprite_size', 'type', 'rarity',
                         'rarity_color', 'stats']

file_lock = threading.Lock()

# region Various dict functions
def get_rarity_color(rarity):
    rarity_dict = dict()
    rarity_dict['Common'] = 'White'
    rarity_dict['Uncommon'] = 'Green'
    rarity_dict['Rare'] = 'Yellow'
    rarity_dict['Legendary'] = 'Purple'
    return rarity_dict.get(rarity)


def get_shape_size(shape):
    tmp = get_item_shape_array(str(shape))
    if tmp is not None:
        shape = tmp

    height = len(shape)
    width = len(shape[0])
    dims = (height, width)

    shape_size = dict()
    shape_size[(1, 1)] = '60x60px'
    shape_size[(1, 2)] = '108x108px'
    shape_size[(1, 3)] = '156x156px'
    shape_size[(1, 4)] = '204x204px'
    shape_size[(2, 1)] = '120x120px'
    shape_size[(2, 2)] = '120x120px'
    shape_size[(2, 3)] = '180x180px'
    shape_size[(3, 1)] = '156x156px'
    shape_size[(3, 2)] = '180x180px'

    return shape_size.get(dims)


def get_item_shape_array(shape):
    shape_name = dict()
    shape_name['1x1'] = ['X']
    shape_name['short L flip vertical'] = ['XX', 'X-']
    shape_name['1x2'] = ['X', 'X']
    shape_name['2x1'] = ['XX']
    shape_name['1x3'] = ['X', 'X', 'X']
    shape_name['2x2'] = ['XX', 'XX']
    shape_name['split'] = ['X-X']
    shape_name[' 1x2 slant backward'] = ['-X', 'X-']
    shape_name['shape_name[1x2 slant forward'] = ['X-', '-X']
    shape_name['Berserkers Club'] = ['-X', '-X', 'X-']
    shape_name['short L flip horizontal'] = ['-X', 'XX']
    shape_name['short T flip'] = ['-X-', 'XXX']
    shape_name['1x4'] = ['X', 'X', 'X', 'X']
    shape_name['short L flip both'] = ['XX', '-X']
    shape_name['3x1'] = ['XXX']
    shape_name['L flip vertical'] = ['XX', 'X-', 'X-']
    shape_name['2x2 slant backward'] = ['-XX', 'XX-']
    shape_name['oboe'] = ['-X', 'X-', 'X-']
    shape_name['short T'] = ['XXX', '-X-']
    shape_name['3x2'] = ['XX', 'XX', 'XX']
    shape_name['T'] = ['XXX', '-X-', '-X-']
    shape_name['short L'] = ['X-', 'XX']
    return shape_name.get(shape)


def get_item_shape_word(shape):
    shape = str(shape)
    shape_array = dict()
    shape_array["['X']"] = '1x1'
    shape_array["['XX', 'X-']"] = 'short L flip vertical'
    shape_array["['X', 'X']"] = '1x2'
    shape_array["['XX']"] = '2x1'
    shape_array["['X', 'X', 'X']"] = '1x3'
    shape_array["['XX', 'XX']"] = '2x2'
    shape_array["['X-X']"] = 'split'
    shape_array["['-X', 'X-']"] = '1x2 slant backward'
    shape_array["['X-', '-X']"] = ' 1x2 slant forward'
    shape_array["['-X', '-X', 'X-']"] = 'Berserkers Club'
    shape_array["['-X', 'XX']"] = 'short L flip horizontal'
    shape_array["['-X-', 'XXX']"] = 'short T flip'
    shape_array["['X', 'X', 'X', 'X']"] = '1x4'
    shape_array["['XX', '-X']"] = 'short L flip both'
    shape_array["['XXX']"] = '3x1'
    shape_array["['XX', 'X-', 'X-']"] = 'L flip vertical'
    shape_array["['-XX', 'XX-']"] = '2x2 slant backward'
    shape_array["['-X', 'X-', 'X-']"] = 'oboe'
    shape_array["['XXX', '-X-']"] = 'short T'
    shape_array["['XX', 'XX', 'XX']"] = '3x2'
    shape_array["['XXX', '-X-', '-X-']"] = 'T'
    shape_array["['X-', 'XX']"] = 'short L'
    return shape_array.get(shape)

    # endregion


def insert_keyword_icons(string):
    # damage is special
    keyword_icons = ['Freeze', 'Energy', 'Rage', 'Haste', 'Weak', 'Slow', 'Spikes', 'Poison', 'Burn', 'Charm', 'Max HP',
                     'HP', 'Gold', 'Curse', 'Dodge', 'Regen', 'Anchored', 'Conductive', 'Heavy', 'Exhaust', 'Discarded',
                     'Piercing', 'Luck', 'Mana', 'Vampierism', 'Float', 'Projectile', 'Disabled']
    for x in keyword_icons:
        string = re.sub(x, '[[File:' + x + '.png|30x30px]] ' + x.lower(), string, flags=re.IGNORECASE)
    string = re.sub('(?<! on )damage', '[[File:Attack.png|30x30px]] damage', string, flags=re.IGNORECASE)
    string = re.sub('block(?!quote)', '[[File:Block.png|30x30px]]', string, flags=re.IGNORECASE)
    return string


class ItemManager:

    def __init__(self, site, image_cache):
        self.item_cache_file = Path('./item_cache.txt')
        self.item_data_file = Path('./itemData.json')
        self.image_cache = image_cache
        self.site = site
        self.items_cache = dict()
        self.items = self.read_item_file()
        self.read_cache_file()

    def normalize_name(self, item):
        if isinstance(item, dict):
            return item['name']
        elif isinstance(item, str):
            return item

    def get_json_item(self, item):
        if isinstance(item, dict):
            return item
        elif isinstance(item, str):
            items = [x for x in self.items if x['name'] == item]
            if len(items) != 1:
                return None
            else:
                return items[0]

    def read_item_file(self):
        with open(self.item_data_file) as myfile:
            json_dict = json.load(myfile)
        item_dict = json_dict['items']
        version_number = json_dict['version']
        for x in item_dict:
            x['version'] = version_number
            x['wikitext'] = self.item_to_wikitext(x)
            x['hash'] = Utils.get_hash_string(x['wikitext'])

        return item_dict

    def item_cache_info(self, item):
        item_name = self.normalize_name(item)
        remote_hash, stored_time = self.items_cache[item_name]
        yesterday = datetime.now() - timedelta(1)
        if stored_time < yesterday.timestamp():
            self.update_item(item_name)
        remote_hash, stored_time = self.items_cache[item_name]
        return remote_hash

    def add_item_to_cache(self, item):
        if isinstance(item, list):
            for x in item:
                self.add_item(x)
        elif isinstance(item, dict):
            item_name = self.normalize_name(item)
            remote_hash, time = self.items_cache[item_name]
            self.items_cache[item_name] = (remote_hash, Utils.get_now_unix())

    def remove_item(self, item):
        self.items_cache.pop(item)

    def update_item(self, item, delay_write=False):
        item = self.get_json_item(item)
        item_name = self.normalize_name(item)
        if item in self.items:
            self.items_cache[item_name] = (
                self.get_web_hash(item), Utils.get_now_unix())
        else:
            self.add_item(item)
        if not delay_write:
            self.write_cache_file()

    def write_cache_file(self):
        with open(str(self.item_cache_file), 'w') as file:
            for key, cache_value in self.items_cache.items():
                remote_hash, cache_time = cache_value
                file.write(str(key) + '=' + str(remote_hash) + ',' + str(cache_time) + '\n')
        return

    def read_cache_file(self):
        if not self.item_cache_file.exists():
            return
        with open(str(self.item_cache_file), 'r') as file:
            lines = file.readlines()
        for line in lines:
            key, cache_value = line.split('=')
            remote_hash, cache_time = cache_value.split(',')
            self.items_cache[key] = (str(remote_hash), float(cache_time))

    def get_web_hashes(self):
        for idx, item in enumerate(self.items):
            if (idx + 1) % 100 == 0:
                self.write_cache_file()
                print(str(idx) + ' of ' + str(len(self.items)))
            self.update_item(item, delay_write=True)
        self.write_cache_file()

    def get_web_hash(self, item):
        item = self.get_json_item(item)
        item_name = self.normalize_name(item)
        page = pywikibot.Page(self.site, item_name)
        if page.exists():
            try:
                comment = page.latest_revision.comment
                if 'Text_Hash=' in comment:
                    return comment.split('=')[1]

                return Utils.get_hash_string(page.text)
            except:
                return None
        else:
            return None

    def item_to_wikitext(self, item):
        item = self.get_json_item(item)
        passive_item = False
        output = dict()
        output = Utils.dict_defaulter(output, wikitext_fancy_fields)
        output['name'] = item['name']
        output['sprite_size'] = self.image_cache.get_sprite_size(item)

        output['shape'] = get_item_shape_word(item['shape'])
        output['shape_size'] = get_shape_size(item['shape'])
        icons_string = ''
        use_cost_str = ''
        both_cost = False
        if len(item['useCost']) != 0:
            if 'energy' in item['useCost']:
                use_cost_str += ' Energy Cost ' + str(item['useCost']['energy'])
                both_cost = True
            if 'mana' in item['useCost']:
                if both_cost:
                    icons_string = 'Mana Cost ' + str(item['useCost']['mana'])
                else:
                    use_cost_str += ' Mana Cost ' + str(item['useCost']['mana'])
        else:
            passive_item = True
        output['use_cost'] = use_cost_str
        output['rarity'] = item['rarity']
        output['rarity_color'] = get_rarity_color(item['rarity'])
        type_string = ''
        for x in item['types']:
            type_string += x + ' <br/> '
        type_string = Utils.rear_replace(type_string, '<br/>', '', 1)
        output['type'] = type_string

        stats_string = ''
        for line in item['descriptions']:
            for header, value in line.items():
                if header == '':
                    for x in value:
                        stats_string += str(x) + '<br/> \n'
                else:
                    stats_string += str(header) + ':\n'
                    for x in value:
                        stats_string += '<blockquote> \n' + str(x) + '<br/> \n </blockquote> \n'

        stats_string = Utils.rear_replace(stats_string, '<br/>', '', 1)
        stats_string = insert_keyword_icons(stats_string)
        stats_string = Utils.rear_replace(stats_string, '\n', '', 1)
        output['stats'] = stats_string

        if 'movable' in item['special']:
            icons_string += 'movable.png'
        if 'alternate use' in stats_string.lower():
            icons_string += 'alternate.png'

        output['icons'] = icons_string

        if passive_item:
            string = '{{' + wikitext_passive_template.format(**output) + '}}'
        else:
            string = '{{' + wikitext_fancy_template.format(**output) + '}}'

        catagories_string = '\n[[Category:Items]]'

        for x in item['types']:
            catagories_string += ' \n[[Category:' + x + ']] '
        if len(item['validChar']) == 1:
            catagories_string += ' \n[[Category:' + item['validChar'][0] + ' Exclusive Items]]'

        return string + catagories_string

    def update_status_now(self, page, exception):
        self.get_web_hash(page.title())
        self.write_cache_file()


    def update_page(self, item, always=False,force=False, delay_write=False):

        item = self.get_json_item(item)
        item_name = self.normalize_name(item)

        if item['hash'] == self.item_cache_info(item) and not always:
            return

        item_page = pywikibot.Page(self.site, item_name)

        item_page.text = item['wikitext']

        try:
            summary = 'Item updated to ' + item['version'] + ' Hash_Text=' + item['hash']
            item_page.save(summary, force=force)
            print('Updating page ' + str(item['name']) + ' success')

            if not delay_write:
                self.write_cache_file()
        except:
            print('Error in updating page' + item['name'])
