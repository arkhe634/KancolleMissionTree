from requests import get
from lxml.html import fromstring, tostring, HtmlElement
from re import match, search
from sys import stderr, argv as args
from enum import Enum
from json import dumps, JSONEncoder

mission_url = "https://wikiwiki.jp/kancolle/%E4%BB%BB%E5%8B%99"


def get_raw(tag):
	return "".join(tag.itertext())


class Period(Enum):
	Once = 0
	Daily = 1
	Weekly = 2
	Monthly = 3
	Quarterly = 4
	Specific = 5


class MissionEncoder(JSONEncoder):
	def default(self, o):
		if isinstance(o, Period):
			return str(o.name)
		return super(MissionEncoder, self).default(o)


def get_mission_period(mission_id, dependency_text):
	specific_mission_id_table = {"Bd4", "Bd6"}
	if mission_id in specific_mission_id_table:
		return Period.Specific
	if "d" in mission_id or "デイリー" in dependency_text:
		return Period.Daily
	if "w" in mission_id or "ウィークリー" in dependency_text:
		return Period.Weekly
	if "m" in mission_id or "マンスリー" in dependency_text:
		return Period.Monthly
	if "q" in mission_id or "クォータリー" in dependency_text:
		return Period.Quarterly
	return Period.Once


def get_items(td):
	rawresult = []
	item = ""
	for child in td.xpath("node()"):
		if (isinstance(child, HtmlElement)):
			if child.tag == "br":
				rawresult.append(item)
				item = ""
			else:
				item += get_raw(child)
		else:
			item += child
	rawresult.append(item)
	result = []
	flag = True
	for item in rawresult:
		if "選択報酬" in item:
			result.append([])
		elif item == "確定報酬":
			flag = False
		elif len(result) == 0:
			result.append(item)
		elif isinstance(result[-1], list) and flag:
			result[-1].append(item)
		else:
			result.append(item)
	return result


def get_mission_dependency(dependency_text: str, prev_id):
	# 依存するミッションを放り込む
	dependency = []

	# ミッションIDにマッチする正規表現
	pattern = "\([a-zA-Z0-9]+\)"
	# ミッションは"及び"で分割できる
	dependency_texts = dependency_text.split("及び")
	for text in dependency_texts:
		result = search(pattern, text)
		verified = not (text.find("要確認") != -1 or text.find("要検証") != -1 or text.find("検証中") != -1)
		if result is not None:
			# ミッションIDが見つかったとき
			dependency.append({"id": result.group()[1:-1], "verified": verified, "text": text})
		elif "↑" in text:
			dependency.append({"id": prev_id, "verified": verified, "text": text})
		else:
			# その他 "検証中"的なテキスト
			dependency.append({"id": "", "verified": verified, "text": text})
	return dependency


def missions_from_table(table):
	missions = {}
	trs = table.xpath("tbody/tr[td[9]]")

	prev_id = "undefined"
	mission_id = "undefined"
	dependency_text = "undefined"

	for mission in trs:
		tds = mission.xpath("td")
		if len(tds) == 9:
			text = get_raw(tds[8])
			# 解放条件か実装日がない場合
			if not match("[0-9]+(/[0-9]+)*", text):
				# 実装日がなかった場合
				dependency_text = text
				prev_id = mission_id
		elif len(tds) == 10:
			dependency_text = get_raw(tds[8])
			prev_id = mission_id
		else:
			print("unknown number of 'td' in table", file=stderr)
			exit(1)
		mission_id = tds[0].text
		mission_name = get_raw(tds[1])
		mission_overview = get_raw(tds[2])
		mission_fuel = get_raw(tds[3])
		mission_magazine = get_raw(tds[4])
		mission_steel = get_raw(tds[5])
		mission_bauxite = get_raw(tds[6])
		mission_items = get_items(tds[7])
		mission_dependency = get_mission_dependency(dependency_text, prev_id)
		mission_period = get_mission_period(mission_id, mission_dependency)
		missions[mission_id] = \
			{
				"id": mission_id,
				"name": mission_name,
				"overview": mission_overview,
				"fuel": mission_fuel,
				"magazine": mission_magazine,
				"steel": mission_steel,
				"bauxite": mission_bauxite,
				"items": mission_items,
				"dependency": mission_dependency,
				"period": mission_period
			}
	return missions


if __name__ == '__main__':
	html = fromstring(get(mission_url).content.decode("UTF-8"))
	# プレイ可能なミッションテーブル集合
	playable = html.xpath(
		"//table[@class='style_table' and thead and not(tbody/tr/th/@colspan) and not(preceding::h2[contains(text(),'終了済み')])]")
	# 終了済みのミッションテーブル集合
	closed = html.xpath(
		"//table[@class='style_table' and thead and not(tbody/tr/th/@colspan) and preceding::h2[contains(text(),'終了済み')]]")
	missions = {}
	for table in playable:
		for key, value in missions_from_table(table).items():
			missions[key] = value
	with open(args[1], "w", encoding="UTF-8") as f:
		f.write(dumps(missions, ensure_ascii=False, indent=4, cls=MissionEncoder))
