function readFile(path) {
    var f = new File(path);
    f.open('r');
    var i = 0;
    var strings = [];
    while (!f.eof) {
        var string = f.readln();
        strings.push(string);
    }
    f.close();
}

function parseTranscript(strings) {
    var lines = [];
    var times = [];
    for (var j = 0; j < strings.length; j++) {
        var line = strings[j];
        if (line == "") {
            continue;
        }
        if (j % 2 == 0) {
            times.push(line);
        } else {
            lines.push(line);
        }
    }

    var transcript = [];
    var i;
    for (i = 0; i < lines.length; i++) {
        var line = lines[i];
        var startTime = times[i];
        var endTime = times[i + 1];
        var lineObj = { text: line, startTime: parseFloat(startTime), endTime: parseFloat(endTime) };
        transcript.push(lineObj);
    }

    return transcript;
}

function getComp(name) {
    var comp;
    for (var i = 1; i <= app.project.numItems; i++) {
        if ((app.project.item(i) instanceof CompItem) && (app.project.item(i).name === name)) {
            comp = app.project.item(i);
            break;
        }
    }
    return comp;
}

function changeText(comp, layerName, text) {
    // alert(layerName);
    var layer = comp.layer(layerName);
    var textProp = layer.property("Source Text");
    var textDocument = textProp.value;
    textDocument.text = text;
    textProp.setValue(textDocument);
}

function scanPropGroupProperties(propGroup) {

    var i, prop;

    // Iterate over the specified property group's properties
    for (i = 1; i <= propGroup.numProperties; i++) {
        prop = propGroup.property(i);
        if (prop.propertyType === PropertyType.PROPERTY)    // Found a property
        {
            // Found a property
            // FYI: layer markers have a prop.matchName = "ADBE Marker"
            // $.writeln(prop.matchName + "NAME: " + prop.name);
            alert(prop.matchName + "NAME: " + prop.name);
        }
        else if ((prop.propertyType === PropertyType.INDEXED_GROUP) || (prop.propertyType === PropertyType.NAMED_GROUP)) {
            // $.writeln("NEW GROUP: " + prop.matchName + "NAME: " + prop.name);
            // Found an indexed or named group, so check its nested properties
            scanPropGroupProperties(prop);
        }
    }
}

function addTextLine(comp, text, startTime, endTime, num) {
    var textLayer = comp.layer("TextTemplate");
    var layerName = "Text " + num;

    var layer = comp.layer(layerName);
    if (layer) {
        layer.remove();
    }
    var newText = textLayer.duplicate();
    newText.name = layerName;
    var selector = newText.property("ADBE Text Properties").property("ADBE Text Animators").property("ADBE Text Animator").property("ADBE Text Selectors").property("ADBE Text Selector");

    var startSelector = selector.property("ADBE Text Percent Start");
    newText.startTime = startTime;
    newText.outPoint = endTime;
    changeText(comp, newText.name, text);
    startSelector.setValueAtTime(startTime, 0);
    var textEndTime = startTime + (endTime - startTime) * 0.75;
    startSelector.setValueAtTime(textEndTime, 100);

}

function clearText(comp) {
    for (var i = 0; i < 30; i++) {
        var layerName = "Text " + i;

        var layer = comp.layer(layerName);
        if (layer) {
            layer.remove();
        }
    }
}


function openTemplate(path) {
    //  if(app.project.file == null){
    var trailer = new File(path);
    app.open(trailer)
    //}
}

function addOrReplace(comp, asset, layerName) {
    var layer = comp.layer(layerName);
    if (layer) {
        layer.remove();
    }
    layer = comp.layers.add(asset);
    layer.name = layerName;
    return layer;
}

function center(comp, layerName) {
    var layer = comp.layer(layerName);
    var property = layer.property("Position");
    var t = 0;
    var nKeys = property.numKeys;
    var rect = layer.sourceRectAtTime(t, false);
    var pos = layer.property("Position").value;
    var scale = layer.property("Scale").value / 100;
    var x = pos[0] + rect.left * scale[0] + rect.width / 2 * scale[0];
    var deltaX = comp.width / 2 - x;
    for (var i = 0; i < property.numKeys; i++) {
        var time = property.keyTime(i + 1);
        property.setValueAtTime(time, pos + [deltaX, 0, 0]);
    }
    if (nKeys == 0) {
        property.setValueAtTime(0, pos + [deltaX, 0, 0]);
    }
}



function render(name, subtitle, episodeNumber, audioName, transcript, outputName, render) {
    var comp = getComp("Intro");
    changeText(comp, "Name", name);
    center(comp, "Name");
    for (var i = 1; i < 5; i++) {
        var layerName = "Occupation";
        if (i > 1) {
            layerName += " " + i;
        }
        changeText(comp, layerName, subtitle);
        center(comp, layerName);
    }
    var numberName = "#" + episodeNumber + " " + name;

    // Change the background
    // var nBgs = 4;
    // choice = (episodeNumber % nBgs) + 1;
    // for(var i=1; i <= nBgs; i++){
    //     var background = comp.layer("Background" + i);
    //     if(choice == i){
    //         background.enabled = true;
    //     }else{
    //         background.enabled = false;
    //     }
    // }


    var trailer = getComp("Trailer");
    changeText(trailer, "Episode & Name", numberName);

    clearText(trailer);
    for (var i = 0; i < transcript.length; i++) {
        line = transcript[i];
        addTextLine(trailer, line.text, line.startTime, line.endTime, i);
    }



    // Importing a audio and background image

    app.beginUndoGroup("Import file");
    var folder = app.project.file.parent;
    folder.changePath('Audio');
    var audioPath = folder.getFiles(audioName);
    // var imagePath = assetFolder + backgroundName;
    var importOpts = new ImportOptions(File(audioPath));
    var audioImport = app.project.importFile(importOpts);
    // importOpts = new ImportOptions(File(imagePath));
    // var imageImport = app.project.importFile(importOpts);

    var audio = addOrReplace(trailer, audioImport, "Audio");
    //Replace image graphics
    // var background = trailer.layer("Background");
    // background.replaceSource(imageImport, false);
    // background.outPoint = audio.source.duration;
    // trailer.layer("Episode").outPoint = audio.source.duration;

    app.endUndoGroup();



    // Setting audio to the waveform
    var audioLayerPropName = "ADBE AudSpect-0001";
    var audioWave = trailer.layer("Waveform");
    audioWave.outPoint = audio.source.duration;
    var waveProp = audioWave.property("Effects").property("ADBE AudSpect").property(audioLayerPropName);
    waveProp.setValue(audio.index);

    //Setting the duration of the trailer to duration of the audio
    trailer.duration = audio.source.duration;

    // Setting up the resulting composition
    var finalMovie = getComp("Combined");
    var trailerLayer = addOrReplace(finalMovie, trailer, "Trailer");
    var introLayer = finalMovie.layer("Intro");
    trailerLayer.startTime = introLayer.outPoint;
    var startTime = trailerLayer.outPoint;
    var endLayer = finalMovie.layer("End");
    endLayer.startTime = startTime;
    var finalMovieDuration = endLayer.outPoint;
    finalMovie.duration = finalMovieDuration;

    if (parseInt(render) == 0) {
        return;
    }
    // app.project.save(new File(template_folder + outputName + ".aep"));
    rq_item = app.project.renderQueue.items.add(finalMovie);
    rq_item.outputModule(1).file = File(assetFolder + outputName + ".mov");
    app.project.renderQueue.queueInAME(true);
    //app.project.renderQueue.render()
}

function render_from_file(name, company, occupation, episodeNumber, textName, audioName, backgroundName, outputName, assetFolder, templateFolder, useOpenProject, render_enabled) {
    if (parseInt(useOpenProject) == 0) {
        openTemplate(templateFolder);
    }
    transcriptPath = assetFolder + textName;
    var strings = readFile(transcriptPath);
    transcript = parseTranscript(strings);
    var subtitle = occupation + " | " + company;
    render(name, subtitle, episodeNumber, audioName, transcript, outputName, render_enabled);
}
