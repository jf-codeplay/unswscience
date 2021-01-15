# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from extract_experience.process_html import execute


class ExperiencePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('experience'):
            adapter['experience'] = execute(adapter['experience'], adapter['name'])
        else:
            adapter['experience'] = None
        return item
