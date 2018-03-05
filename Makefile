.PHONY:all
all:
	@mkdir -p html
	@mkdir -p data
	@curl http://wikiwiki.jp/kancolle/?%C7%A4%CC%B3 -o html/mission.html
	@nkf -w --overwrite html/mission.html
	@python3 script/scraper.py html/mission.html data/missions.json
