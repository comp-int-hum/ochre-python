function initializeAudioInteraction(elem){
    var rbut = htmx.find(elem, ".record");
    var pbut = htmx.find(elem, ".play");
    var ubut = htmx.find(elem, ".upload");
    var inp = htmx.find(elem, "input");
    var out = htmx.find(elem, "span");
    ubut.addEventListener("click", (event) => {
	inp.click();
    });
	if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
	    const constraints = { audio: true };
	    navigator.mediaDevices.getUserMedia(constraints).then(
		(stream) => {
		    const mediaRecorder = new MediaRecorder(stream, {audioBitsPerSecond: 44100});
		    rbut.onclick = () => {
			if(mediaRecorder.state == "recording"){
			    mediaRecorder.stop();
			    console.log(mediaRecorder.state);
			    console.log("recorder stopped");			    
			    rbut.style.background = "";
			    rbut.style.color = "white";
			}
			else{
			    mediaRecorder.start();
			    console.log(mediaRecorder.state);
			    console.log("recorder started");
			    console.error(rbut.style.background);
			    rbut.style.background = "red";
			    rbut.style.color = "black";
			}
		    };

		    mediaRecorder.ondataavailable = function(event) {
			var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
			var formData = new FormData();
			formData.append("data", event.data, "file.flac");
			$.ajax(
			    {
				headers: {
				    Accept : "application/json",
				    "X-CSRFToken" : csrftoken
				},
				url: inp.parentElement.parentElement.getAttribute("endpoint_url"),
				method: "POST",
				data: formData,
				success: function (data){
				    out.textContent = "Transcript: " + data["transcript"];
				},
				contentType: false,
				processData: false,
				async: true
			    }
			)
		    }
		}
	    ).catch(
		(err) => {
		    console.error("error");
		}
	    );
	}

    inp.addEventListener("change", (event) => {
	var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
	var formData = new FormData();
	var input = event.target;
	formData.append("data", event.target.files[0], event.target.files[0].name);
	$.ajax(
	    {
		headers: {
		    Accept : "application/json",
		    "X-CSRFToken" : csrftoken
		},
		url: input.parentElement.parentElement.getAttribute("endpoint_url"),
		method: "POST",
		data: formData,
		success: function (data){
		    out.textContent = "Transcript: " + data["transcript"];
		},
		contentType: false,
		processData: false,
		async: true
	    }
	)
    })
    	    
}			


function updateImageDisplay(event) {
    var input = event.target;
    var detector_type = input.parentElement.getAttribute("detector_type");
    var preview = input.parentElement.getElementsByTagName("img")[0];
    var canvas = input.parentElement.getElementsByTagName("canvas")[0];
    var file = input.files[0];
    preview.src = URL.createObjectURL(file);
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    var formData = new FormData();
    formData.append("data", file, file.name);
    $.ajax(
	{
	    headers: {
		Accept : "application/json",
		"X-CSRFToken" : csrftoken
	    },
	    url: input.parentElement.getAttribute("endpoint_url"),
	    method: "POST",
	    data: formData,
	    success: function (data){
		//console.error(data);
		var jdata = data; //JSON.parse(data);
		//if(detector_type == "object"){
		    var width = preview.naturalWidth;
		    var height = preview.naturalHeight;		
		    var scaleWidth = 800 / width;
		    var scaleHeight = 600 / height;
		    var scale;
		    if(scaleWidth > scaleHeight){
			scale = scaleWidth;
		    }
		    else{
			scale = scaleHeight;
		    }
		    var fontSize = Math.round(32 / scale);
		    canvas.width = width * scale;
		    canvas.height = height * scale;
		    var ctx = canvas.getContext("2d");
		    ctx.scale(scale, scale);
		    ctx.drawImage(preview, 0, 0);
		    for(let box of jdata){
			var name;
			var score;
			var bounds;
			for(var key in box){
			    if(box.hasOwnProperty(key)){
				var val = box[key];
				if(key == "score"){
				    score = val;
				}
				else{
				    name = key;
				    bounds = val;
				}
				/*else if(key == "label"){
				    name = val;
				}
				else if(key == "bounding_box"){
				    bounds = val;
				}*/
			    }
			}
			if(score > 0.8){
			    ctx.strokeStyle = "rgb(200,0,0)";
			    ctx.lineWidth = 2.0;
			    ctx.strokeRect(bounds[0], bounds[1], bounds[2] - bounds[0], bounds[3] - bounds[1]);
			    ctx.fillStyle = "rgb(200,0,0)";
			    ctx.font = fontSize.toString() + "px serif";
			    ctx.fillText(name + "=" + score.toPrecision(3), bounds[0], bounds[1]);
			}
		    }
		//}
		/*
		else if(detector_type == "text"){
		    var width = preview.naturalWidth;
		    var height = preview.naturalHeight;		
		    var scaleWidth = 80 / width;
		    var scaleHeight = 60 / height;
		    var scale;
		    if(scaleWidth > scaleHeight){
			scale = scaleWidth;
		    }
		    else{
			scale = scaleHeight;
		    }
		    var fontSize = Math.round(32 / scale);
		    canvas.width = width * scale;
		    canvas.height = height * scale;
		    var ctx = canvas.getContext("2d");
		    ctx.scale(scale, scale);
		    ctx.drawImage(preview, 0, 0);
			var name;
			var score;
			var bounds;
			for(var key in jdata){
			    if(jdata.hasOwnProperty(key)){
				var val = jdata[key];
				if(key == "probability"){
				    score = val;
				}
				else if(key == "text"){
				    name = val;
				}
				else if(key == "bounding_box"){
				    bounds = val;
				}
			    }
			}
			if(score > 0.8){
			    ctx.strokeStyle = "rgb(200,0,0)";
			    ctx.lineWidth = 2.0;
			    ctx.strokeRect(bounds[0], bounds[1], bounds[2] - bounds[0], bounds[3] - bounds[1]);
			    ctx.fillStyle = "rgb(200,0,0)";
			    ctx.font = fontSize.toString() + "px serif";
			    ctx.fillText(name, bounds[0], bounds[1] + (bounds[3] - bounds[1]));
			}

		}*/
	    },
	    contentType: false,
            processData: false,
	    async: true
	}
    );
}


function findAll(item, query){
    var retval = Array.from(htmx.findAll(item, query));
    for(let el of htmx.findAll(item.parentElement, query)){
	if(el.id == item.id){
	    retval.push(item);
	}
    }
    return retval;
}

function getList(name){
    var retval = sessionStorage.getItem(name);
    if(retval == null){
	retval = []
    }
    else{
	retval = JSON.parse(retval);
    }
    console.info("Returning value of", name, ":", retval);
    return retval;
}

function setList(name, value){
    console.info("Setting value of", name, "to", value);
    sessionStorage.setItem(name, JSON.stringify(value));
}

function setValue(name, value){
    console.info("Setting value of", name, "to", value);
    sessionStorage.setItem(name, JSON.stringify(value));    
}

function getValue(name){
    console.info("Getting value of", name);
    return JSON.parse(sessionStorage.getItem(name));
}

function checkValue(name, value){
    var retval = getList(name).includes(value);
    console.info("Checking if value", value, "is in", name, ":", retval);    
    return retval
}

function removeValue(name, value){
    console.info("Removing value", value, "from", name);
    var cur = getList(name);
    setList(name, cur.filter(c => c != value));
}

function addValue(name, value){
    var cur = getList(name);
    if(!(cur.includes(value))){
	cur.push(value);
    }
    console.info("Adding value", value, "to", name);
    setList(name, cur);
}

function removeNestedValues(element){
    console.info("Unsetting all accordions and tabs underneath", element.id);
    for(let el of element.getElementsByClassName("ochre-accordion-item")){
	collapseAccordionItem(el);
    }
    for(let el of element.getElementsByClassName("ochre-tab-button")){
	unsetTab(el);
    }
}

function removeAccordionItem(item){
    console.info("Completely removing accordion item", item.id);
    removeValue("active_accordion_items", item.id);
    item.remove();
}

function collapseAccordionItem(item){
    console.info("Collapsing accordion item", item.id);
    var button = item.querySelector(".ochre-accordion-header > .btn-group > .ochre-accordion-button");
    var content = document.getElementById(button.getAttribute("aria-controls"));
    button.setAttribute("aria-expanded", "false");
    button.classList.add("collapsed");
    content.classList.add("collapse");
    content.classList.remove("show");
    removeValue("active_accordion_items", item.id);
    removeNestedValues(item);
}

function setFirstTab(tabs){
    setTab(htmx.find(tabs, "li > button"));
}

function expandAccordionItem(item){
    console.info("Expanding accordion item", item.id);
    var button = item.querySelector(".ochre-accordion-header > div.btn-group > button.accordion-button");
    // This is also a problem: (and now that I've forgotten the reason for this comment: why would button ever be null?)
    if(button != null){
	var content = document.getElementById(button.getAttribute("aria-controls"));
	button.setAttribute("aria-expanded", "true");
	button.classList.remove("collapsed");
	content.classList.remove("collapse");
	content.classList.add("show");
	addValue("active_accordion_items", item.id);
	for(let tabs of item.getElementsByClassName(".ochre-nav-tabs")){
	    setFirstTab(tabs);
	}
	item.scrollIntoView(true);
    }
}

function setTab(tab){
    console.info("Activating tab", tab.id);
    var content = document.getElementById(tab.getAttribute("aria-controls"));
    tab.setAttribute("aria-selected", "true");
    tab.classList.add("active");
    content.classList.add("show");
    content.classList.add("active");   
    addValue("active_tab_items", tab.id);
    //tab.scrollIntoView(true);
}

function unsetTab(tab){
    console.info("Deactivating tab", tab.id);    
    var content = document.getElementById(tab.getAttribute("aria-controls"));
    tab.setAttribute("aria-selected", "false");
    tab.classList.remove("active");
    content.classList.remove("show");
    content.classList.remove("active");   
    removeValue("active_tab_items", tab.id);
    removeNestedValues(content);
}

function refreshAccordionItem(item){    
    console.error("Unimplemented: refreshAccordionItem");
}

// another reminder of how bad this is!
function saveState(){
    console.info("Saving scroll state of page");
    var pathName = document.location.pathname;
    var scrollPosition = $(document).scrollTop();
    sessionStorage.setItem("scrollPosition_" + pathName, scrollPosition.toString());
}

function restoreState(root){
    console.info("Restoring state below", root.id);
    for(let acc of findAll(root, ".ochre-accordion")){
	var activeCount = 0;
	for(let item of acc.children){
	    if(checkValue("active_accordion_items", item.id) == true && activeCount == 0){
		expandAccordionItem(item);		
		activeCount += 1;
	    }
	    else if(item.classList.contains("ochre-accordion-item")){
		collapseAccordionItem(item);
	    }
	}	
    }    
    for(let ct of root.getElementsByClassName("ochre-accordion-collapse")){
	ct.addEventListener("hide.bs.collapse", event => {
	    removeValue("active_accordion_items", event.target.parentElement.id);
	    removeNestedValues(event.target.parentElement);
	});
	ct.addEventListener("show.bs.collapse", event => {
	    for(let el of event.target.parentElement.parentElement.children){
		if(el.id != event.target.parentElement.id){
		    collapseAccordionItem(el);
		}
	    }
	    expandAccordionItem(event.target.parentElement);	    
	    for(let el of event.target.parentElement.getElementsByClassName("ochre-nav-tabs")){
		setFirstTab(el);
	    }
	});	
    }
    for(let tabs of htmx.findAll(root, ".ochre-nav-tabs")){
	var activeCount = 0;
	for(let tab of htmx.findAll(tabs, "li > button")){
	    if(checkValue("active_tab_items", tab.id) == true && activeCount == 0){
		setTab(tab);
		activeCount += 1;
	    }
	    else{
		unsetTab(tab);
	    }
	}
	if(activeCount == 0){
	    setFirstTab(tabs);
	}
    }
    for(let el of root.getElementsByClassName("ochre-tab-button")){
        el.addEventListener("show.bs.tab", event => { addValue("active_tab_items", event.target.id); });
	el.addEventListener("hide.bs.tab", event => { removeValue("active_tab_items", event.target.id) });
    }

}

var colors = [[235, 172, 35], [184, 0, 88], [0, 140, 249], [0, 110, 0], [0, 187, 173], [209, 99, 230], [178, 69, 2], [255, 146, 135], [89, 84, 214], [0, 198, 248], [135, 133, 0], [0, 167, 108], [189, 189, 189]];

function ochreSetup(root, htmxSwap){
    console.info("Performing initial setup on", root.id);
    var sheet = (function() {
	// Create the <style> tag
	var style = document.createElement("style");
	style.setAttribute("href", "palette");
	style.appendChild(document.createTextNode(""));
	document.head.appendChild(style);
	return style.sheet;
    })();

    for(let i of Array(10).keys()){
	var rgb = colors[i];
	sheet.insertRule(".topic" + i + " {background:rgb("+ rgb[0] + "," + rgb[1] + "," + rgb[2] + ");}");
    }



    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
	return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // things that should only happen once, at the top level of the page
    //if(!htmxSwap){
    // preserve accordion, tab, and scroll states when browsing away from or reloading the page
    // this is bad! see just above!
    
    //}

    // restore any previous state (must happen for htmx-loaded fragments too)
    restoreState(root);

    //const tooltipTriggerList = root.querySelectorAll('[data-bs-toggle="tooltip"]')
    //const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    
    for(let el of htmx.findAll(root, ".ochre-select")){
	el.addEventListener("change", event => {
	    var tgt = document.getElementById(event.target.value);
	    htmx.trigger(tgt, "select");
	});
/*	el.parentElement.addEventListener("keyup", (event) => {
	    if(event.key == "Tab" && event.shiftKey == true){
		console.error("dsadsa");
	    }
	}, true);*/
    }
    
    for(let el of htmx.findAll(root, ".ochre-image-interaction")){
	el.addEventListener('change', updateImageDisplay);
    }
    
    for(let el of htmx.findAll(root, ".ochre-audio-interaction")){
	initializeAudioInteraction(el);
	//el.addEventListener('change', updateImageDisplay);	
    }

    if(root.parentNode != null && root.classList.contains("ochre-select")){
	root.addEventListener("change", event => {
	    var tgt = document.getElementById(event.target.value);
	    htmx.trigger(tgt, "select");
	});
    }
    
    // run initialization for Monaco editor widgets
    for(let el of htmx.findAll(root, ".ochre-editor")){
	var actEl = htmx.find(el.parentElement, ".ochre-editor-action");
	if(el.getAttribute("processed") != "true"){
	    require.config(
		{
		    paths: {
			vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.34.0-dev.20220625/min/vs'
		    }
		}
	    );
	    require(
		['vs/editor/editor.main'],
		function () {
		    var value = JSON.parse(
			document.getElementById(el.getAttribute("value_id")).textContent
		    );
		    var form = el.parentNode;
		    var language = el.getAttribute("language");
		    var readOnly = el.getAttribute("readonly") == "true";
		    var editor = monaco.editor.create(
			el,
			{	      
			    value: value,
			    language: language,
			    automaticLayout: true,
			    tabCompletion: "on",
			    wordWrap: true,
			    codeLens: false,
			    minimap: false,
			    readOnly: readOnly,
			    domReadOnly: readOnly
			}
		    );
		    if(language == "markdown"){
			editor.addAction({
			    id: "upload-image",
			    label: "Upload or link existing image",
			    precondition: null,
			    keybindingContext: null,
			    contextMenuGroupId: "navigation",
			    run: function (ed){
				var dialog = document.createElement("dialog");
				var div = document.createElement("div");
				div.setAttribute("hx-get", "/api/file/");
				div.setAttribute("hx-headers", "{\"Accept\" : \"text/html include=true\", \"interaction-mode\" : \"view\", \"interaction-context\" : \"list\"}");
				div.setAttribute("hx-trigger", "intersect");
				div.setAttribute("hx-swap", "outerHTML");
				htmx.process(div);
				dialog.appendChild(div);
				document.body.appendChild(dialog);
				dialog.addEventListener("close", () => {
				    if(dialog.returnValue){
					console.error(dialog.returnValue);
					var model = ed.getModel();
					var pos = ed.getPosition();
					model.pushEditOperations(
					    [],
					    [
						{
						    range: {
							startColumn: pos.column,
							endColumn: pos.column,
							startLineNumber: pos.lineNumber,
							endLineNumber: pos.lineNumber},
						    text: "![](" + dialog.returnValue + ")"
						}
					    ],
					    () => null
					);
				    }
				    
				});
				dialog.showModal();
			    }
			});
			editor.addAction({
			    id: "upload-file",
			    label: "Upload or link existing file",
			    precondition: null,
			    keybindingContext: null,
			    contextMenuGroupId: "navigation",
			    run: function (ed){
				var dialog = document.createElement("dialog");
				var div = document.createElement("div");
				div.setAttribute("hx-get", "/api/file/");
				div.setAttribute("hx-headers", "{\"Accept\" : \"text/html include=true\", \"interaction-context\" : \"list\", \"interaction-mode\" : \"view\"}");
				div.setAttribute("hx-trigger", "intersect");
				div.setAttribute("hx-swap", "outerHTML");
				htmx.process(div);
				dialog.appendChild(div);
				document.body.appendChild(dialog);
				dialog.addEventListener("close", () => {
				    if(dialog.returnValue){
					console.error(dialog.returnValue);
					var model = ed.getModel();
					var pos = ed.getPosition();
					model.pushEditOperations(
					    [],
					    [
						{
						    range: {
							startColumn: pos.column,
							endColumn: pos.column,
							startLineNumber: pos.lineNumber,
							endLineNumber: pos.lineNumber},
						    text: "[](" + dialog.returnValue + ")"
						}
					    ],
					    () => null
					);
				    }
				    
				});
				dialog.showModal();
			    }
			});
		    }
		    el.addEventListener(
			"keyup",
			(event) => {
			    var content = editor.getModel().getValue();
			    if(event.key == "Tab" && event.shiftKey == true){
				var info = event.target.parentElement.parentElement.parentElement;
				var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
				$.ajax(
				    {
					headers: {
					    Accept : "application/json",
					    "X-CSRFToken" : csrftoken,
					},
					url: info.getAttribute("endpoint_url"),
					method: "POST",
					data: {data: content},
					success: function (data){
					    var output = data;
					    var model = editor.getModel();
					    var current = model.getValue();
					    var newValue = "";
					    var decorations = [];
					    for(let item of output){
						var value = item["token"];
						console.error(item);
						var interp = " ";
						if(newValue.length == 0){
						    interp = "";
						}
						var start = newValue.length + interp.length;
						newValue += interp + value;
						var end = newValue.length;
						if(item["label"] != false && item["label"] != undefined){
						    decorations.push([item["label"], start, end]);
						}
					    }
					    model.setValue(newValue);
					    var pos = model.getPositionAt(
						model.getValue().length
					    );
					    editor.setPosition(pos);
					    var actualDecorations = []
					    for(let dec of decorations){
						var start = model.getPositionAt(dec[1]);
						var end = model.getPositionAt(dec[2]);
						var topic = dec[0];
						actualDecorations.push(
						    {
							range: new monaco.Range(
							    start.lineNumber,
							    start.column,
							    end.lineNumber,
							    end.column
							),
							options:{
							    className: "topic" + topic,
							    hoverMessage: "topic" + topic,
							    stickiness: 1
							}
						    }
						);
					    }
					    editor.deltaDecorations(
						[],
						actualDecorations
					    );
					}
				    }
				);
			    }
			}			
		    );		
		    editor.getModel().onDidChangeContent(
			(event) => {
			    var content = editor.getModel().getValue();
			    var hid = document.getElementById(
				el.getAttribute("value_id") + "-hidden"
			    );
			    hid.setAttribute("value", content);
			}
		    );
		}
	    );
	    el.setAttribute("processed", "true");
	}
    }
    
    // initialize annotated documents
    var elms=root.getElementsByClassName("labeled-token");
    for(var i=0;i<elms.length;i++){
	elms[i].onmousedown = function(event){
	    var targetClass = Array.from(event.target.classList.values()).find(el => el.startsWith("topic"));
            for(var k=0;k<elms.length;k++){
		if(elms[k].classList.contains(targetClass)){
		    elms[k].classList.toggle("selected");
		}
		else{
		    elms[k].classList.remove("selected");
		}
            }
	}
	elms[i].onmouseenter = function(event){
	    var targetClass = Array.from(event.target.classList.values()).find(el => el.startsWith("topic"));
            for(var k=0;k<elms.length;k++){
		if(elms[k].classList.contains(targetClass)){
		    elms[k].classList.toggle("highlighted");
		}
		else{
		    elms[k].classList.remove("highlighted");
		}
            }
	}
	elms[i].onmouseexit = function(event){
	var targetClass = Array.from(event.target.classList.values()).find(el => el.startsWith("topic"));
            for(var k=0;k<elms.length;k++){
		if(elms[k].classList.contains(targetClass)){
		    elms[k].classList.toggle("highlighted");
		}
		else{
		    elms[k].classList.remove("highlighted");
		}
            }
	}
    }

    for(let el of htmx.findAll(root, ".ochre-carousel")){
	var carousel = new bootstrap.Carousel(el);
	carousel.cycle();
    }
}


function handleOchreEvent(event){
    var event_type = event.detail.event_type;
    var object_class = event.detail.object_class;
    var model_class = event.detail.model_class;
    console.info("Handling event of type", event_type, ", object class", object_class, ", model class", model_class);
    location.reload(true);

    /*
    if(event_type == "delete"){

	for(let el of document.getElementsByClassName(object_class)){
	    removeAccordionItem(el);
	}
    }
    else if(event_type == "update"){
	for(let el of document.getElementsByClassName("ochre-accordion-item")){
	    if(
		app_label == el.getAttribute("app") &&
		    model_name == el.getAttribute("model_name") &&
		    pk == el.getAttribute("pk")
	    ){
		//console.error("(not yet) refreshing", el);
		// refresh
	    }
	}	
    }
    else if(event_type == "create"){
    var model_url = event.detail.model_url;
    */
	//var accItem = event.target.parentElement.parentElement.parentElement.parentElement;
	/*
	$.ajax(
	    {		
		url: model_url,
		headers: {"include" : true},
		success: function (data){
		    var dummy = document.createElement( 'html' );
		    dummy.innerHTML = data;
		    for(let el of dummy.getElementsByClassName(object_class)){
			for(let tgt of document.getElementsByClassName(model_class)){
			    //console.error(el, tgt);
			    //var accItem = htmx.closest(tgt, ".accordion-item");
			    tgt.insertAdjacentElement("beforeend", el);
			    ochreSetup(el, true);
			    //dummy.remove();
			    //var rel = document.getElementById(el.id);
			    //for(let ch of accItem.children){
			    //htmx.trigger(ch, "refreshForm");
			    //}
			    //collapseAccordionItem(accItem);
			    //for(let ch of el.querySelectorAll("*[hx-trigger='intersect']")){
			    //htmx.trigger(ch, "intersect");
			    //}
			    //expandAccordionItem(accItem);
			    //expandAccordionItem(el);
			    //htmx.trigger(el, 
			    restoreEditingState();
			    
			}
		    }		    
		},
		dataType: "html"
	    }
	);
	*/

	//console.error(model_url);
	/*var accItem = event.target.parentElement.parentElement.parentElement.parentElement;
	var acc = accItem.parentElement;
	  $.ajax(
	    {		
		url: acc.getAttribute("accordion_url"),
		success: function (data){
		    var dummy = document.createElement( 'html' );
		    dummy.innerHTML = data;
		    for(let el of dummy.getElementsByClassName("ochre-accordion-item")){			
			if(el.getAttribute("app_label") == app_label && el.getAttribute("model_name") == model_name && el.getAttribute("pk") == pk)
			{
			    acc.insertBefore(el, accItem);
			    htmx.process(el);
			    ochreSetup(el, true);
			    dummy.remove();
			    var rel = document.getElementById(el.id);
			    for(let ch of accItem.children){
				htmx.trigger(ch, "refreshForm");
			    }
			    collapseAccordionItem(accItem);
			    for(let ch of el.querySelectorAll("*[hx-trigger='intersect']")){
				htmx.trigger(ch, "intersect");
			    }
			    expandAccordionItem(el);
			}			
		    }		    
		},
		dataType: "html"
	    }
	  );
	  */

	/*
	  Adding new item to other accordions requires some thought w.r.t. identifiers
	accItem.insertAdjacentElement("beforestart", newItem);
	
	for(let otherAcc of htmx.findAll(".ochre-accordion")){
	    if(otherAcc.getAttribute("id") != acc.getAttribute("id")){
		if(otherAcc.getAttribute("app_label") == app_label && otherAcc.getAttribute("model_name") == model_name){
		    var added = false;
		    for(let item of otherAcc.children){
			if(item.getAttribute("create") == "true"){
			    // insert before element and break
			    item.insertAdjacentElement("beforebegin", accItem);
			    added = true;
			    if(isExpanded(item)){
				collapseAccordionItem(item);			
				expandAccordionItem(accItem);
			    }
			    break;
			}		    
		    }
		    if(added == false){
			// insert at end of accordion
			acc.insertAdjacentElement("beforeend", newItem);
		    }

		    }
	    }
	}
	*/		    
/*	
    }
    else{
	console.warn("Unknown OCHRE event type:", event_type);
    }
*/
}




document.body.addEventListener('htmx:beforeSwap', function(evt) {
    //console.error(evt);
  // Allow 422 and 400 responses to swap
  // We treat these as form validation errors
  if (evt.detail.xhr.status === 422 || evt.detail.xhr.status === 400) {
    evt.detail.shouldSwap = true;
    evt.detail.isError = false;
  }
});
