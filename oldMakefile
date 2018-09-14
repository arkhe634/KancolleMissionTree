.PHONY:update html/mission.html


update:index.html js/functions.js

index.html: svg/dependency.svg script/transform.py
	@python3 script/transform.py svg/dependency.svg index.html

svg/dependency.svg:dot/dependency.dot
	@dot -Tsvg dot/dependency.dot -o svg/dependency.svg

pdf/dependency.pdf:dot/dependency.dot
	@dot -Tpdf dot/dependency.dot -o pdf/dependency.pdf

dot/dependency.dot:data/missions.json script/graph.py
	@python3 script/graph.py data/missions.json dot/dependency.dot

data/missions.json:html/mission.html script/scraper.py
	@python3 script/scraper.py html/mission.html data/missions.json

html/mission.html:
	@curl https://wikiwiki.jp/kancolle/%E4%BB%BB%E5%8B%99 -o html/mission.html
	@nkf -w --overwrite html/mission.html

js/functions.js:ts/functions.ts
	tsc --target es6 ts/functions.ts -outFile js/functions.js
	
	
	
