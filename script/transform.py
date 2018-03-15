from sys import argv as args,exit
from bs4 import BeautifulSoup,Doctype

if __name__ == "__main__":
	if not len(args) == 3:
		exit(1)
	with open(args[1],'r') as inputFile:
		soup = BeautifulSoup(inputFile,"lxml")
		html = BeautifulSoup("","html5lib")
		html.contents.insert(0,Doctype("html"))
		html.contents[1]["lang"]="ja"

		meta = html.new_tag("meta")
		meta["charset"]="UTF-8"
		html.contents[1].head.contents.append(meta)

		script = html.new_tag("script")
		script["type"]="text/javascript"
		script["src"]="js/functions.js"
		html.contents[1].head.contents.append(script)

		svg = soup.find("svg")

		html.contents[1].body.contents.append(svg)

		nodes = svg.find_all("g",class_="node")
		for node in nodes:
			node["onclick"]="onClick(this);"
		with open(args[2],'w') as outputFile:
			outputFile.write(str(html)+"\n")
