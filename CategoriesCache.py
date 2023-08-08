from datetime import datetime, timedelta
from pathlib import Path
import Utils
import pywikibot

def get_json_categories(items):
    categories = set()
    for item in items:
        for type in item['types']:
            if type not in categories:
                categories.add(type)
    return list(categories)


class CategoriesManager:

    def __init__(self, site):
        self.category_cache_file = Path('./category_cache.txt')
        self.site = site
        self.categories = dict()
        self.read_cache_file()

    def category_value(self, category):
        value, stored_time = self.categories[category]
        yesterday = datetime.now() - timedelta(1)
        if stored_time < yesterday.timestamp():
            self.get_web_categories()
        value, stored_time = self.categories[category]
        return value

    def add_category(self, category, value=False):
        if isinstance(category, str):
            self.categories.setdefault(category, (value, Utils.get_now_unix()))
        elif isinstance(category, list):
            for x in category:
                self.add_category(x)

    def remove_category(self, category):
        self.categories.pop(category)

    def update_category(self, category, value):
        if category in self.categories.keys():
            cache_value, cache_time = self.categories[category]
            now = Utils.get_now_unix()
            if now >= cache_time:
                self.categories[category] = (value, now)
        else:
            self.add_category(category, value)

    def write_cache_file(self):
        with open(str(self.category_cache_file), 'w') as file:
            for key, cache_value in self.categories.items():
                value, time = cache_value
                file.write(str(key) + '=' + str(value) + ',' + str(time) + '\n')
        return

    def read_cache_file(self):
        if not self.category_cache_file.exists():
            return
        with open(str(self.category_cache_file), 'r') as file:
            lines = file.readlines()
        for line in lines:
            key, cache_value = line.split('=')
            value, time = cache_value.split(',')
            tv = False
            if 'True' in value:
                tv = True
            self.categories[key] = (tv, float(time))

    def get_web_categories(self):
        page = pywikibot.Category(self.site, 'Items')
        sub_categories_iter = page.subcategories(recurse=1)
        for x in sub_categories_iter:
            self.update_category(x.title().replace('Category:', ''), True)
        self.write_cache_file()
        return

    def update_web_category(self, category, delay_write=False):
        if not self.category_value(category):
            page = pywikibot.Category(self.site, category)
            page.text = '[[Category:Items]]'
            page.save()
            self.update_category(category, True)
            if not delay_write:
                self.write_cache_file()
            return

    def update_web_categories(self):
        for category in self.categories.keys():
            if not self.category_value(category):
                self.update_web_category(category, delay_write=True)

            self.write_cache_file()

    def remove_web_category(self, category, delay_write=False):
        page = pywikibot.Page(self.site, category)
        page.delete(reason='unused category', prompt=False)
        self.categories[category] = (False, Utils.get_now_unix())
        if not delay_write:
            self.write_cache_file()

    def remove_unused_web_categories(self):
        categories = pywikibot.Category(self.site, 'Items')
        for category in categories.subcategories(recurse=1):
            if isinstance(category, pywikibot.Category):
                articles = category.articles()
                if len(articles) < 1:
                    self.remove_web_category(category.title(), delay_write=True)
        self.write_cache_file()
