from sys import argv as args,exit,stderr
from json import loads,dump

def getColor(id,period):
	if id[0] == 'A':
		return "#008000"
	if id[0] == 'B':
		return "#FF4500"
	if id[0] == 'C':
		return "#B8D200"
	if id[0] == 'D':
		return "#90CDF1"
	if id[0] == 'E':
		return "#EBD842"
	if id[0] == 'F':
		return "#98623C"
	if id[0] == 'G':
		return "#9932CC"
	if id[0] == 'W':
		return "#FF69B4"
	if id[0] == '5':
		return "#CD619B"
	stderr.write(f'Unknown mission id {id}\n')
	return "#FFFFFF"

def edge(f,id,data):
	name = data["name"]
	fuel = data["fuel"]
	magazine = data["magazine"]
	steel = data["steel"]
	bauxite = data["bauxite"]
	others = data["items"]
	dependency = data["dependency"]
	period = data["period"]
	for mission in dependency:
		if not len(mission["id"])==0:
			f.write(f'\tM{mission["id"]}->M{id};\n')

def node(f,id,data):
	name = data["name"]
	fuel = data["fuel"]
	magazine = data["magazine"]
	steel = data["steel"]
	bauxite = data["bauxite"]
	others = data["items"]
	dependency = data["dependency"]
	period = data["period"]
	f.write(f'\tM{id}[shape="record",style="filled",id="{id}",label="{{{name}|{{{fuel}|{magazine}|{steel}|{bauxite}}}')
	for items in others:
		f.write('|')
		if isinstance(items,list):
			f.write(f'{{{"|".join(items)}}}')
		else:
			f.write(items)
	f.write(f'}}",fillcolor="{getColor(id,period)}"];\n')

def write(f,missions):
	f.write('digraph d{\n')
	for id,data in missions.items():
		node(f,id,data)
	f.write("\n")
	for id,data in missions.items():
		edge(f,id,data)
	f.write('}\n')


if __name__ == '__main__':
	if not len(args) == 3:
		exit(1)
	with open(args[1],'r') as inputf:
		data = loads(inputf.read())
		with open(args[2],'w') as f:
			write(f,data)