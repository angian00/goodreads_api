#!/usr/bin/env python3

import requests
from requests_oauthlib import OAuth1Session

import xml.etree.ElementTree

import json
import csv
import time


user_id = "37957418" #angian
shelf = "read"

key_file = "keys.json"
shelves_file = "reviews.csv"



def main():
	global oauth

	with open(key_file) as f:
		key_data = json.load(f)
	
	oauth = OAuth1Session(key_data["api_key"], client_secret = key_data["api_secret"],
		resource_owner_key = key_data["access_token"],
		resource_owner_secret = key_data["access_token_secret"]
	)

	print_reviews()
	#update_shelves()


def print_reviews():
	all_reviews = []
	page = 1

	while True:
		if page > 1:
			time.sleep(1)

		print("Getting page #{}".format(page))
		resp = oauth.get("https://www.goodreads.com/review/list", 
			params={'v': 2, 'format': 'xml', 'id': user_id, 'shelf': shelf, 'page': page, 'per_page': 200})

		resp_dom = xml.etree.ElementTree.fromstring(resp.content)

		new_reviews = resp_dom.findall("./reviews/review")
		if not new_reviews:
			break

		for r in new_reviews:
			shelves = []
			all_reviews.append({
				"book_id": r.find("./book/id").text,
				"title": r.find("./book/title").text, 
				"shelves": [ s.get("name") for s in r.findall("./shelves/shelf") ]
			})

		page = page + 1


	with open(shelves_file, "w+") as f:
		f.write("book_id|title|shelves\n")
		for r in all_reviews:
			if len(r["shelves"]) != 1:
				continue
			print_review(r, f)

		
def print_review(r, f):
	#book, shelves
	#print("[{}] [{}]".format(k, v))
	shelves = r["shelves"]
	shelves.remove("read")
	shelves_str = ",".join(shelves)
	f.write("{}|{}|{}\n".format(r["book_id"], r["title"], shelves_str))


def update_shelves(gc=None):
	shelves = {}

	with open(shelves_file) as f:
		dr = csv.DictReader(f, delimiter='|')
		for row in dr:
			if row["shelves"] == "":
				continue

			curr_shelves = row["shelves"].split(",")
			for s in curr_shelves:
				if s not in shelves:
					shelves[s] = []

				shelves[s].append(row["book_id"])

	#print(shelves)

	for s in shelves:
		books_str = ",".join(shelves[s])
		print("{} <-- {}".format(s, books_str))

		resp = oauth.post("https://www.goodreads.com/shelf/add_books_to_shelves.xml", 
			data={'shelves': [s], 'bookids': books_str})
		print(resp.status_code)
		time.sleep(1)

if __name__ == '__main__':
	main()
