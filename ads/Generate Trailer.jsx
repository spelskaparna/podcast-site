
//@include "automate.jsx"
var settings = readSettings();

function r(episodeNumber, transcript){
    var episode = settings['episodes'][episodeNumber -1]; 
    var name = episode['name'];
    var subtitle = episode['subtitle'];
    var audioName = episodeNumber + ".mp3";
    var outputName = episodeNumber;
    var render_enabled = 0;
    transcript = transcript.replace("\r","").split("\n");
    transcript = parseTranscript(transcript);
    render(name, subtitle, episodeNumber, audioName, transcript, outputName, render_enabled);

}

function readSettings(){
    var folder = app.project.file.parent;
    var path = folder.getFiles("settings.json");
    var f = new File(path);
    f.open('r');
    var settings;
    while (!f.eof) {
        settings = f.read();
    }
    return JSON.parse(settings);
}

var w = new Window("dialog", "Are you sure?", undefined, { "closeButton": true });
w.orientation = "column";
var items = settings['titles'];
var dropdown = w.add("dropdownlist", undefined, items);

var groupOne = w.add("group", undefined, "groupOne");
groupOne.add("statictext", undefined, "Are you sure?");

var editText = groupOne.add("edittext", { x: 0, y: 0, width: 800, height: 400 }, "", { multiline: true });
var groupTwo = w.add("group", undefined, "groupTwo");
var buttonYes = groupTwo.add("button", undefined, "Run");

buttonYes.onClick = function () {
    var text = editText.text;
    var episode = dropdown.selection.index;
    w.hide();
    r(episode + 1, text);
}


w.show();   
