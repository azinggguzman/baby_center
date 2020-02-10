# -*- coding: utf-8 -*-

import scrapy
from datetime import datetime


class PeripartumSpider(scrapy.Spider):
    name = 'babyctr'

    start_urls = ['https://community.babycenter.com/groups/a15325/postpartum_depression_anxiety_and_related_topics']

    def parse(self, response):
        for post_link in response.xpath('//*[@id="group-discussions"]/div[3]/div/div/a/@href').extract():
            link = response.urljoin(post_link)
            yield scrapy.Request(link, callback=self.parse_thread)


        next_page = response.xpath('//*[@class= "page-link next"]/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)


        # Going into each post and extracting information.

    def parse_thread(self, response):
        original_post = response.xpath("//*[@class='__messageContent fr-element fr-view']/p/text()").extract()
        title = response.xpath("//*[@class='discussion-original-post__title']/text()").extract_first()
        author_name = response.xpath("//*[@class='discussion-original-post__author__name']/text()").extract_first()
        unixtime = response.xpath("//*[@class='discussion-original-post__author__updated']/@data-date").extract_first()
        unixtime2 = (int(unixtime))/1000 # Removing milliseconds
        timestamp = datetime.utcfromtimestamp(unixtime2).strftime("%m/%d/%Y %H:%M")
        number_comments = response.xpath("//*[@class='discussion-replies__header__comments']/text()").extract()
        #replies_list = response.xpath("//*[@class='discussion-replies__list']").getall()
        yield {
            "title": title,
            "date": timestamp,
            "author_name": author_name,
            "post": original_post,
            "comments": number_comments}

        # Getting the comments and their information for each post

        reply_post = response.xpath(".//*[@class='wte-reply__content__message __messageContent fr-element fr-view']/p/text()").extract()
        reply_author = response.xpath("//*[@class='wte-reply__author__name']/text()").extract()
        reply_time = response.xpath("//*[@class='wte-reply__author__updated']/@data-date").extract()
        timestamp_replies = []
        for reply in reply_time:
            reply_date = (int(reply)) / 1000  # Removing milliseconds
            reply_timestamp = datetime.utcfromtimestamp(reply_date).strftime("%m/%d/%Y %H:%M")
            timestamp_replies.append(reply_timestamp)

        reply_pairs = zip(reply_author, reply_post, timestamp_replies)

        for x, y, z in reply_pairs:
            yield{
                "title" : title,
                "date" : z,
                "author_name" : x,
                "post": y,
                "comments": '0 Comments'

            }
