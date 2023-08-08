import re

import pywikibot

import CategoriesCache
import ImageCache
import ItemCache
import Utils

image_cache = None
category_cache = None
item_cache = None


# -1 if older is actually older
def version_number_comparator(old_version: str, new_version: str):
    older_patching = 'live'
    new_patching = 'live'
    older_numerics = old_version[1:]
    new_numerics = new_version[1:]
    if old_version.find('-') is not None:
        older_numerics, older_patching = old_version[1:].split('-')
    if new_version.find('-') is not None:
        new_numerics, new_patching = new_version[1:].split('-')

    old_nums = map(int, older_numerics.split('.'))
    new_nums = map(int, new_numerics.split('.'))
    sl = len(old_nums)

    if len(old_nums) > len(new_nums):
        sl = len(new_nums)

    for x in range(sl):
        check = old_nums[x] - new_nums[x]
        if check != 0:
            return check
    if older_patching < new_patching:
        return -1
    if older_patching == new_patching:
        return 0
    return 1


def main():
    site = pywikibot.Site('en', 'bph')
    global image_cache
    image_cache = ImageCache.ImageManager(site)
    global category_cache
    category_cache = CategoriesCache.CategoriesManager(site)
    global item_cache
    item_cache = ItemCache.ItemManager(site, image_cache)


    relics = [x['name'] for x in item_cache.items if 'Relic' in x['types']]
    for x in relics:
        item_cache.update_page(x)
    item_cache.update_page('Ace Cleaver')
    item_cache.update_item('Ace Cleaver')
    page = pywikibot.Page(site, 'Ace Cleaver')
    rev = page.latest_revision
    print('')




    # update_page(site, new_item_dict[0])
    # p = Path('./sprites/Whip_701.png')
    #
    # force_upload_image(site, p, new_name='TestFile.png')
    #
    # for x in new_item_dict:
    #     if x['shape'] not in shapes:
    #         shapes.append(x['shape'])
    #     if 'pet' in x['types'] and x['validChar'] != ['Pochette']:
    #         print(x['name'])
    #
    # for x in shapes:
    #     print(str(x) + '\n')

    # upload_needed_sprites(site,new_item_dict)

    # page = pywikibot.Page(site, 'Cleaver')
    # edit = page.text.replace("this line was added via a code, feel free to delete this line -Aj14325",'this line was added via code, feel free to delete it -Aj14325')
    # page.put(edit,summary= 'This is a test edit with code, feel free to delete this line -Aj14325')\

    # version_number, new_item_dict = convert_json_to_dict('itemData.json')
    #
    # old_item_list = get_current_item_list()
    #
    # item_update_list = [x for x in new_item_dict if item_changed(x,old_item_list) == True]
    # new_item_list = [x for x in new_item_dict if item_changed(x,old_item_list) is None]


if __name__ == '__main__':
    main()
    # [['X'], ['-', 'X'], ['XX', 'X-'], ['X', 'X'], ['XX-'], ['XX', 'XX'], ['X', 'X', 'X'], ['X-X'], ['-X', 'X-'], ['XX'], ['-', 'X', 'X'], ['--', 'XX', 'XX'], ['X-', '-X'], ['-X', '-X', 'X-'], ['-X', 'XX'], ['---', 'XXX'], ['--', 'X-'], ['---', 'XX-', 'XX-'], ['X-', 'X-'], ['X-'], ['-', 'X', 'X', 'X'], ['X-', 'X-', 'X-'], ['-X-', 'XXX'], ['XX-', 'XX-', 'XX-'], ['X', 'X', 'X', 'X'], ['-', 'X', 'X', 'X', 'X'], ['XX', '-X'], ['--', 'XX'], ['XX', 'X-', 'X-'], ['XX', 'XX', 'XX'], ['-XX', 'XX-'], ['---', 'XXX', 'XXX'], ['---', 'XX-', 'X--'], ['-X', 'X-', 'X-'], ['XXX', 'XXX'], ['XXX', '-X-'], ['XXX'], ['XXX', '-X-', '-X-'], ['X-', 'XX']]
