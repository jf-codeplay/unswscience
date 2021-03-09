import scrapy
from unswscience.items import UnswscienceItem


class StafftmpdataSpider(scrapy.Spider):
    name = 'stafftmpdata'
    allowed_domains = ['research.unsw.edu.au']
    start_urls = ['https://research.unsw.edu.au/researcher?faculty=Faculty%20of%20Science']

    def parse(self, response):
        nextpageurl = response.xpath("//a[@title='Go to next page']/@href")
        yield from self.scrape(response)
        if nextpageurl:
            # If we've found a pattern which matches
            path = nextpageurl.extract_first()
            nextpage = response.urljoin(path)
            print("Found url: {}".format(nextpage))  # Write a debug statement
            yield scrapy.Request(nextpage, callback=self.parse)  # Return a call to the function "parse"
        # yield from self.scrape(response)

    def scrape(self, response):
        for resource in response.xpath("//div/div/div[@class = 'info']"):
            item = UnswscienceItem()
            item["name"] = resource.xpath("./a[@class ='title']/text()").extract_first().strip()
            link_to_profile = resource.xpath("./a[@class ='title']/@href").extract_first()
            item["link"] = response.urljoin(link_to_profile)
            request = scrapy.Request(item["link"], callback=self.get_experience)
            request.meta['item'] = item
            yield request

    def get_experience(self, response):
        self.logger.info('Got successful response from {}'.format(response.url))
        item = response.meta['item']
        # style_1 = "//h2[text()='Biography']/following-sibling::div/div/ul"
        # style_2 = "//h2[text()='Professional Experience']/following-sibling::/ul"
        # style_3 =
        # if response.xpath(style_1) or response.xpath(style_2):
        #     item["experience"] = [resource.xpath("./li/text()").extract_first() for resource in response.xpath(style_1)]
        full_xpath_bio = "//h2[text()='Biography']/following-sibling::div[@class = 'body-full']/div[@class = 'field-bio']"
        if response.xpath(full_xpath_bio):
            biography = response.xpath(full_xpath_bio).extract_first() or ''
        else:
            biography = response.xpath("//h2[text()='Biography']/following-sibling::div[@class = 'field-bio']").extract_first() or ''
        xpath_quali = "//h2[text()='My Qualifications']/following-sibling::div[@class = 'field-my-qualifications']"
        qualification = response.xpath(xpath_quali).extract_first() or ''
        if biography or qualification:
            item["experience"] = "<br>".join([biography, qualification])
        xpath_image = "//div[@class = 'profile-indent']/div[@class = 'image']/picture/source[1]/@srcset"
        item["image"] = response.urljoin(response.xpath(xpath_image).extract_first())
        yield item
