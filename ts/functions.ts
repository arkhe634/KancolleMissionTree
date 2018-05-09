document.oncontextmenu = function () { return false; }

function evaluate(xpath: string, root: Node = document): Element[] {
	const result: XPathResult = document.evaluate(xpath, root, undefined, XPathResult.ANY_TYPE, undefined);
	const ret: Element[] = [];
	let node: Node = result.iterateNext();
	while (node) {
		if (node instanceof Element)
			ret.push(node);
		node = result.iterateNext();
	}
	return ret;
}

document.addEventListener("DOMContentLoaded", () => {
	let nodes: Element[] = evaluate("//*[@class='node']");
	let edges: Element[] = evaluate("//*[@class='edge']");
	for (let node of nodes) {
		let id = node.attributes["id"].value;
		let color = evaluate("./*[name()='polygon']", node)[0].attributes["fill"].value;
		DefaultColor[id] = color;
		Nodes[id] = node as HTMLElement;
		Dependency[id] = [];
	}
	for (let edge of edges) {
		let [from, to] = evaluate("./*[name()='title']", edge)[0].textContent.split("->");
		console.log(to);
		Dependency[to.substr(1)].push(from.substr(1));
	}
});

//{id:ノード}
let Nodes: { [key: string]: HTMLElement } = {};
//{id:色}
let DefaultColor: { [key: string]: string; } = {};
let CompletedMissions: { [key: string]: HTMLElement } = {};
let CompletedDependency: { [key: string]: HTMLElement[] } = {};
let DisplayedMissions: { [key: string]: HTMLElement } = {};
//{id:[id]}
let Dependency: { [key: string]: string[] } = {};
document.onkeydown = function (e) {
	console.log(e);
};



function setClear(target: HTMLElement, source: HTMLElement): void {
	let id = target.getAttribute("id");
	let polygon = target.getElementsByTagName("polygon")[0] as SVGPolygonElement;

	if (id in CompletedDependency) {
		if (CompletedDependency[id].indexOf(source) != -1) return;
	} else {
		CompletedDependency[id] = [];
	}
	CompletedDependency[id].push(source);
	polygon.style.fill = "#FFFFFF";
	for (let depends of Dependency[id]) {
		setClear(Nodes[depends], source);
	}
}
function unsetClear(target: HTMLElement, source: HTMLElement): void {
	let id = target.getAttribute("id");
	let polygon = target.getElementsByTagName("polygon")[0] as SVGPolygonElement;
	if (!(id in CompletedDependency)) return;
	CompletedDependency[id].splice(CompletedDependency[id].indexOf(source), 1);
	if (CompletedDependency[id].length == 0) {
		delete CompletedDependency[id];
		delete CompletedMissions[id];
		polygon.style.fill = DefaultColor[id];
	}
	for (let depends of Dependency[id]) {
		unsetClear(Nodes[depends], source);
	}
}

function onClick(element: HTMLElement): void {
	let id = element.getAttribute("id");
	if (id in CompletedMissions) return;
	let polygon = element.getElementsByTagName("polygon")[0] as SVGPolygonElement;
	if (id in DisplayedMissions) {
		polygon.style.strokeWidth = "";
		delete DisplayedMissions[id];
		for (let depends of Dependency[id]) {
			unsetClear(Nodes[depends], element);
		}
	} else {
		polygon.style.strokeWidth = "5";
		DisplayedMissions[id] = element;
		for (let depends of Dependency[id]) {
			setClear(Nodes[depends], element);
		}
	}
}
