document.oncontextmenu = function () { return false; };
function evaluate(xpath, root = document) {
    const result = document.evaluate(xpath, root, undefined, XPathResult.ANY_TYPE, undefined);
    const ret = [];
    let node = result.iterateNext();
    while (node) {
        ret.push(node);
        node = result.iterateNext();
    }
    return ret;
}
document.addEventListener("DOMContentLoaded", () => {
    let nodes = evaluate("//*[@class='node']");
    let edges = evaluate("//*[@class='edge']");
    for (let node of nodes) {
        let id = node.attributes["id"].value;
        let color = evaluate("./*[name()='polygon']", node)[0].attributes["fill"].value;
        DefaultColor[id] = color;
        Nodes[id] = node;
        Dependency[id] = [];
    }
    for (let edge of edges) {
        let [from, to] = evaluate("./*[name()='title']", edge)[0].textContent.split("->");
        Dependency[to].push(from);
    }
});
//{id:ノード}
let Nodes = {};
//{id:色}
let DefaultColor = {};
let CompletedMissions = {};
let CompletedDependency = {};
let DisplayedMissions = {};
//{id:[id]}
let Dependency = {};
document.onkeydown = function (e) {
    console.log(e);
};
function setClear(target, source) {
    let id = target.getAttribute("id");
    let polygon = target.getElementsByTagName("polygon")[0];
    if (id in CompletedDependency) {
        if (CompletedDependency[id].indexOf(source) != -1)
            return;
    }
    else {
        CompletedDependency[id] = [];
    }
    CompletedDependency[id].push(source);
    polygon.style.fill = "#FFFFFF";
    for (let depends of Dependency[id]) {
        setClear(Nodes[depends], source);
    }
}
function unsetClear(target, source) {
    let id = target.getAttribute("id");
    let polygon = target.getElementsByTagName("polygon")[0];
    if (!(id in CompletedDependency))
        return;
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
function onClick(element) {
    let id = element.getAttribute("id");
    if (id in CompletedMissions)
        return;
    let polygon = element.getElementsByTagName("polygon")[0];
    if (id in DisplayedMissions) {
        polygon.style.strokeWidth = "";
        delete DisplayedMissions[id];
        for (let depends of Dependency[id]) {
            unsetClear(Nodes[depends], element);
        }
    }
    else {
        polygon.style.strokeWidth = "5";
        DisplayedMissions[id] = element;
        for (let depends of Dependency[id]) {
            setClear(Nodes[depends], element);
        }
    }
}
