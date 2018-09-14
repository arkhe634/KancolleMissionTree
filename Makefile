DIRS = data dot

update:index.html js/functions.js

index.html: svg/dependency.svg script/transform.py
	@python3 script/transform.py svg/dependency.svg index.html

svg/dependency.svg:dot/dependency.dot
	@dot -Tsvg dot/dependency.dot -o svg/dependency.svg

pdf/dependency.pdf:dot/dependency.dot
	@dot -Tpdf dot/dependency.dot -o pdf/dependency.pdf

dot/dependency.dot:data/missions.json script/graph.py dot
	@python3 script/graph.py data/missions.json dot/dependency.dot

data/missions.json:script/main.py data
	@python3 script/main.py $@

$(DIRS):%:
	@mkdir $@

js/functions.js:ts/functions.ts
	tsc --target es6 ts/functions.ts -outFile js/functions.js