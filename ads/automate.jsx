function parseTranscript(path){
    var f = new File(path);
    f.open('r');
    var i = 0;
    var lines = [];
    var times = [];
    while(!f.eof){
        var line = f.readln();
        if(line==""){
            continue;
        }
        if( i % 2 == 0){
            times.push(line);
    }else{
            lines.push(line);
        }
        i++;
    }
    f.close();

    var transcript = [];
    var i;
    for (i = 0; i < lines.length; i++) { 
        var line = lines[i];
        var startTime = times[i];
        var endTime = times[i+1];
        var lineObj = {text:line, startTime:parseFloat(startTime), endTime:parseFloat(endTime)};
        transcript.push(lineObj);
     }
    
    return transcript;
}

function getComp(name){
    var comp;
    for (var i = 1; i <= app.project.numItems; i ++) {
        if ((app.project.item(i) instanceof CompItem) && (app.project.item(i).name === name)) {
            comp = app.project.item(i);
            break;
        }
    }
    return comp;
}

function changeText(comp, layerName, text){
    var layer = comp.layer(layerName);
    var textProp = layer.property("Source Text");
    var textDocument = textProp.value;
    textDocument.text = text;
    textProp.setValue(textDocument);
}

function scanPropGroupProperties(propGroup)
{

    var i, prop;

    // Iterate over the specified property group's properties
    for (i=1; i<=propGroup.numProperties; i++)
    {
        prop = propGroup.property(i);
        if (prop.propertyType === PropertyType.PROPERTY)    // Found a property
        {
            // Found a property
            // FYI: layer markers have a prop.matchName = "ADBE Marker"
            $.writeln(prop.matchName + "NAME: " + prop.name);
        }
        else if ((prop.propertyType === PropertyType.INDEXED_GROUP) || (prop.propertyType === PropertyType.NAMED_GROUP))
        {
            $.writeln("NEW GROUP: " + prop.matchName + "NAME: " + prop.name);
            // Found an indexed or named group, so check its nested properties
            scanPropGroupProperties(prop);
        }
    }
}

function addTextLine(comp, text, startTime, endTime, num){
    var textLayer = comp.layer("TextTemplate");
    var layerName = "Text" + num;

    var layer = comp.layer(layerName);
    if(layer){
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
    var textEndTime = startTime + (endTime - startTime)*0.75;
    startSelector.setValueAtTime(textEndTime, 100);
    
 }


function openTemplate(folder){
  //  if(app.project.file == null){
        var trailer = new File(folder + "Template.aep");
        app.open(trailer)
    //}
}

function addOrReplace(comp, asset, layerName){
    var layer = comp.layer(layerName);
    if(layer){
        layer.remove();
    }
    layer = comp.layers.add(asset); 
    layer.name = layerName;
    return layer; 
}

function render(name, company, occupation, episodeNumber, textName, audioName, backgroundName, outputName,assetFolder, templateFolder, useOpenProject){
    if(parseInt(useOpenProject) == 0){
        openTemplate(templateFolder);
    }
    var comp = getComp ("Intro");
    changeText(comp, "Company", company);
    changeText(comp, "Name", name);
    changeText(comp, "Occupation", occupation);
    var numberName = "#" + episodeNumber + " " + name;
    var trailer = getComp ("Trailer");
    changeText(trailer, "Episode", numberName);
    var end = getComp ("End");   
    changeText(end, "Episode", numberName);
   
   
    
    transcriptPath = assetFolder  + textName;
    transcript = parseTranscript(transcriptPath);
    
    for(var i=0; i < transcript.length; i++){
        line = transcript[i];
        $.writeln(line.startTime);
        addTextLine(trailer, line.text, line.startTime, line.endTime, i);
     }
   

   
    // Importing a audio and background image
    
    app.beginUndoGroup("Import file");  
    var audioPath = assetFolder + audioName;
    var imagePath = assetFolder + backgroundName;
    var importOpts = new ImportOptions(File(audioPath));  
    var audioImport = app.project.importFile(importOpts);
    importOpts = new ImportOptions(File(imagePath));  
    var imageImport = app.project.importFile(importOpts);  
      
    var audio = addOrReplace(trailer, audioImport, "Audio");  
    //Replace image graphics
    var background = trailer.layer("Background");
    background.replaceSource(imageImport, false);
    background.outPoint = audio.source.duration;
    trailer.layer("Episode").outPoint = audio.source.duration;
     
    app.endUndoGroup();  

    
   
    // Setting audio to the waveform
    var audioLayerPropName = "ADBE AudWave-0001";
    var audioWave = trailer.layer("Audio Wave");
    audioWave.outPoint = audio.source.duration;
    var waveProp = audioWave.property("Effects").property("ADBE AudWave").property(audioLayerPropName);
    waveProp.setValue(audio.index);

    //Setting the duration of the trailer to duration of the audio
    trailer.duration = audio.source.duration;

    // Setting up the resulting composition
    var finalMovie = getComp ("Combined");
    var trailerLayer = addOrReplace(finalMovie, trailer, "Trailer");  
    var introLayer = finalMovie.layer("Intro");
    trailerLayer.startTime = introLayer.outPoint;
    var startTime = trailerLayer.outPoint;
    var endLayer = finalMovie.layer("End");
    endLayer.startTime = startTime;
    var finalMovieDuration = endLayer.outPoint;
    finalMovie.duration = finalMovieDuration;
        
    // app.project.save(new File(template_folder + outputName + ".aep"));

    rq_item = app.project.renderQueue.items.add(finalMovie);
    rq_item.outputModule(1).file = File(assetFolder + outputName + ".mov");
    app.project.renderQueue.queueInAME(true);
    //app.project.renderQueue.render()
}


