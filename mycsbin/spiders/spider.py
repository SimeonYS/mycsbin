import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import MmycsbinItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class MmycsbinSpider(scrapy.Spider):
	name = 'mycsbin'
	start_urls = ['https://www.mycsbin.com/blog']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="meta-blog"]/text()').get()
		title = response.xpath('//h2/text()').get()
		content = response.xpath('(//div[@class="std-padding"]//div[@class="col-xs-12"])[2]//text() |//div[@class="col-sm-8"]//text() | //div[@class="col-sm-6"]//text() |//div[contains(@class,"col-sm-")]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=MmycsbinItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
