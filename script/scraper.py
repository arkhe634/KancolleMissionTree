from sys import argv as args,exit
import re,json,io
from bs4 import BeautifulSoup,element

def getRawString(tag):
	return "".join(tag.find_all(text=True))

def getMissionDependency(dependency_text,prev_id):
	#依存するミッションを放り込む
	#dependency[i] = {id:ミッションID,verified:検証中かどうか,text:元の文字列}
	dependency = []

	#ミッションIDにマッチする正規表現
	pattern = "\([a-zA-Z0-9]+\)"
	#ミッションは(多分)"及び"で分割できる
	dependency_texts = dependency_text.split("及び")
	for text in dependency_texts:
		result = re.search(pattern,text)
		verified = not(text.find("要確認")!=-1 or text.find("要検証")!=-1 or text.find("検証中")!=-1)
		if result is not None:
			#ミッションIDが見つかったとき
			dependency.append({"id":result.group()[1:-1],"verified":verified,"text":text})
		elif text.find("↑")!=-1:
			#一つ前のミッション
			dependency.append({"id":prev_id,"verified":verified,"text":text})
		else:
			#"その他(検証中)"みたいなテキスト
			dependency.append({"id":"","verified":verified,"text":text})
	return dependency

def getNewestMissionPeriod(dependency_text):
	if dependency_text.find("デイリー")!=-1:
		return "d"
	if dependency_text.find("ウィークリー")!=-1:
		return "w"
	if dependency_text.find("マンスリー")!=-1:
		return "m"
	if dependency_text.find("クォータリー")!=-1:
		return "q"
	return "o"

def getMissionPeriod(mission_id):
	if mission_id.find("d")!=-1:
		return "d"
	if mission_id.find("w")!=-1:
		return "w"
	if mission_id.find("m")!=-1:
		return "m"
	if mission_id.find("q")!=-1:
		return "q"
	return "o"

def correctTypos(str):
	return str\
		.replace("高速修復剤","高速修復材")\
		.replace("小型電探","")\
		.replace("対空機銃","")\
		.replace("高射装置","")\
		.replace("中口径主砲","")
def getOthers(td):
	flag = False
	skip_strings = \
		["艦上戦闘機","小口径主砲","上陸用舟艇","シークレット家具","局地戦闘機","爆雷","小型電探","艦上攻撃機",
		 "ソナー","対地装備","輸送機材","対空機銃","増設バルジ","水上偵察機","応急修理要員","対艦強化弾",
		 "水上爆撃機","大型探照灯","水上艦要員","注)２","陸軍戦闘機","司令部施設","水上戦闘機","潜水艦魚雷",
		 "噴式戦闘爆撃機","艦上偵察機","補給物資","陸上攻撃機","魚雷","特型内火艇","艦上爆撃機","簡易輸送部材",
		 "大口径主砲","航空要員","対空電探","対水上電探","大型飛行艇","機関部強化","副砲","増設バルジ(中型艦)",
		 "増設バルジ(大型艦)","戦闘糧食"]
	append_strings = ["選択報酬","探照灯","イベント海域","開放","解放","高速修復材","高速修復剤","第2艦隊開放",
					  "第3艦隊開放","第4艦隊開放","駆逐艦"]
	result = []
	str = ""
	for child in td.children:
		if isinstance(child,element.Tag):
			if child.name == "br":
				if not str=="":
					result.append(correctTypos(str))
				str = ""
				continue
			elif child.name=="a":
				str+=child.string
				continue
			elif child.name=="span":
				if child.string is None:
					#print("raw ",getRawString(child))
					str+=getRawString(child)
					continue
				if child.string in skip_strings:
					continue
				if not re.match("("+"|".join(append_strings)+")(x[0-9]+)?|(x[0-9]+)",child.string) and not re.match("★[0-9]+",child.string):
					flag=True
					#print("append ",child.string)
				str+=child.string
				continue
			elif child.name=="strong":
				if child.string=="選択報酬":
					if not str=="":
						result.append(str)
					result.append("選択報酬")
					str=""
					continue
				else:
					try:
						startIndex = [i for i,v in enumerate(result) if isinstance(v,list) or v=="選択報酬"][-1]
					except:
						startIndex=-1
					or_result = list(filter((lambda x:result.index(x)>startIndex),result))
					if startIndex<0 or result[startIndex]=="選択報酬":
						result = list(filter((lambda x:result.index(x)<startIndex),result))
					else:
						result = list(filter((lambda x:result.index(x)<=startIndex),result))
					result.append(or_result)
					continue
		elif isinstance(child,element.NavigableString):
			if child=="[獲]":
				continue
			str += child
			continue
		print(child,type(child))
		exit(1)
	if not str =="":
		result.append(correctTypos(str))
	if flag:
		print(result)
	return result

if __name__ == '__main__':
	if not len(args) == 3:
		exit(1)
	#mission.html
	inputFile = args[1]
	#missions.json
	jsonFile = args[2]
	with open(inputFile) as f:
		html = f.read()
		soup = BeautifulSoup(html,"html.parser")
		#ミッションデータ
		missions = {}
		
		tables = soup.find_all("table",class_="style_table")
		for table in tables:
			#任務娘のボイステーブル
			if table.thead is None:
				continue
			#一番最初のデイリー/ウィークリーのテーブル
			if table.thead.tr.th.string != "ID":
				continue
			#テーブルごとに一回ここにデータを放り込む
			#出撃任務以外の定期任務はIDから識別できないので出撃任務と同じテーブルにあるかどうかで定期任務か判別する
			table_missions = {}
			#単発("o"),デイリー("d"),ウィークリー("w"),マンスリー("m"),クォータリー("q")のフラグ
			regular_mission_flag = "o"
			#x月y日実装分的なテーブルでそれをされると困るので判定を無効化するフラグ
			newest_mission_flag = len(table.tbody.find_all(text=re.compile("実装分")))!=0
			#最後のミッションのid(依存関係解決のときに"↑達成後"を解決するため
			prev_id = "undefined"
			#最後の依存テキスト
			prev_dependency_text = "undefined"
			#依存テキストのrowspanが2とかのときはprev_id/last_dependency_textを更新させない
			life = 1

			for mission_tr in table.tbody.find_all("tr"):
				tds = mission_tr.find_all(recursive=False)
				first_column = tds[0]
				#"マンスリー合計"とかのthタグを除去
				if first_column.name!="td":
					continue
				#x月y日実装分とかのcolspanが任務っぽくないやつを除去
				if first_column.get("colspan") is not None:
					continue
				#行にいくつtdがあるか
				if len(tds)==8:
					#解放条件と実装日が無い場合
					dependency_text = prev_dependency_text
				elif len(tds)==9:
					# 解放条件か実装日がない場合
					text = getRawString(tds[8])
					if re.match("[0-9]+(/[0-9]+)*", text):
						# 解放条件がなかった場合
						dependency_text = prev_dependency_text
					else:
						# 解放条件があった場合
						dependency_text = text
						if tds[8].has_attr("rowspan"):
							life = int(tds[8]["rowspan"])
							prev_dependency_text = dependency_text
						else:
							life = 1
				elif len(tds) == 10:
					# 解放条件も実装日もある場合
					dependency_text = getRawString(tds[8])
					if tds[8].has_attr("rowspan"):
						life = int(tds[8]["rowspan"])
						prev_dependency_text = dependency_text
					else:
						life = 1
				else:
					# 想定外、これが起きるなら他の処理も上手く行ってない可能性が高そう
					sys.stdderr.write("unknown mission table format found.")
				mission_id = getRawString(tds[0])
				mission_name = getRawString(tds[1])
				mission_overview = getRawString(tds[2])
				mission_fuel = getRawString(tds[3])
				mission_magazine = getRawString(tds[4])
				mission_steel = getRawString(tds[5])
				mission_bauxite = getRawString(tds[6])
				mission_others = getOthers(tds[7])
				mission_dependency = getMissionDependency(dependency_text, prev_id)
				mission_period = getNewestMissionPeriod(dependency_text) if newest_mission_flag else getMissionPeriod(
					mission_id)
				if not newest_mission_flag and mission_period != "n":
					regular_mission_flag = mission_period
				# prev_idの更新
				life -= 1
				if life == 0:
					prev_id = mission_id
				# 特定のミッション以外を弾く(イベント任務とか)
				id_pattern = "B[dwmq]?[0-9]+|[ACDEFG][0-9]+|W[ABCF][0-9]+"
				if re.match(id_pattern, mission_id) is None:
					continue
				table_missions[mission_id] = \
					{
						"id": mission_id,
						"name": mission_name,
						"overview": mission_overview,
						"fuel": mission_fuel,
						"magazine": mission_magazine,
						"steel": mission_steel,
						"bauxite": mission_bauxite,
						"others": mission_others,
						"dependency": mission_dependency,
						"period": mission_period
					}
			for key in table_missions.keys():
				if not newest_mission_flag:
					table_missions[key]["period"] = regular_mission_flag
			for key, value in table_missions.items():
				if key in missions.keys():
					if missions[key]["period"] == "o":
						missions[key] = value
				else:
					missions[key] = value
		with io.open(jsonFile,"w",encoding="utf-8") as jf:
			jf.write(json.dumps(missions,ensure_ascii=False,indent=4))
