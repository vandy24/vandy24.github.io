function get_loc() {
  var radius = document.querySelector("#max");
  if(radius.value>50 || radius.value<=0){
	  alert("Your search area is out of bounds. Must be less than 50 Miles and positive.")
	  return;}
  var old = document.querySelector("#results");
  var newtable = document.createElement('tbody');
  newtable.id="results";
  old.parentNode.replaceChild(newtable, old);
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(dummy);
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

function dummy(position){
  var lat = position.coords.latitude;
  var lon = position.coords.longitude;
  get_postings(lat, lon, "http://search.3taps.com/", get_map);
}

async function get_postings(lat, lon, url, callback){
	var radius = document.querySelector("#max");
	var search = document.querySelector("#search");
	uri= url+"?text="+search.value+"&lat="+lat.toString()+"&long="+lon.toString()+"&radius="+radius.value+"mi&retvals=heading,location,price,external_url"+"&sort=distance";
	let opts = {
		method: 'GET',
	}
	let resp = await fetch(uri, opts);
	results = await resp.json();
	callback(results, lat, lon, draw_table);
}

async function get_more_postings(lat, lon, page){
	var radius = document.querySelector("#max");
	var search = document.querySelector("#search");
	uri= "http://search.3taps.com/"+"?text="+search.value+"&lat="+lat.toString()+"&long="+lon.toString()+"&radius="+radius.value+"mi&retvals=heading,location,price,external_url"+"&sort=distance"+"&page="+page;
	let opts = {
		method: 'GET',
	}
	let resp = await fetch(uri, opts);
	results = await resp.json();
	return results;
}

async function get_map(postings, lat, lon, callback){
	var posting = postings["postings"];
	if(posting.length==0){
		alert("Bad news! No local postings of your search!");
		return;
		}
	while(postings["next_page"]!=-1){
		let temp = await get_more_postings(lat, lon, postings["next_page"]);
		posting = posting.concat(temp["postings"]);
		postings["next_page"]=temp["next_page"];
	}
	var body="https://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels?pp="+lat+","+lon+";0;YOU";
	var temp_body=""
	var j=0;
	if(posting.length<100){
		var len=posting.length;}
	else{var len=100;}
	for(var i=0; i<len; i++){
		
		if(i==len-1){
			if(j==i){
				body+="&pp="+posting[i]["location"]["lat"]+","+posting[i]["location"]["long"]+";4;"+i;
				j=i+1;
			}
			else{
				var ji = j.toString()+"-"+i.toString();
				body+="&pp="+posting[i]["location"]["lat"]+","+posting[i]["location"]["long"]+";4;"+ji;
				j=i+1;
			}	
		}
		else if(posting[i]["location"]["lat"]!=posting[i+1]["location"]["lat"] &&
		posting[i]["location"]["long"]!=posting[i+1]["location"]["long"]){
			if(j==i){
				body+="&pp="+posting[i]["location"]["lat"]+","+posting[i]["location"]["long"]+";4;"+i;
				j=i+1;
			}
			else{
				var ji = j.toString()+"-"+i.toString();
				body+="&pp="+posting[i]["location"]["lat"]+","+posting[i]["location"]["long"]+";4;"+ji;
				j=i+1;
			}
		}
	}
	body+="&key=AvWjYu-PKLX_yA_wjaiVhhgn8L4zISfT_zN1cpFjwLyzByKro4crRk6pOE1r8fmI";
	body = body.split('%').join('');
	var xml = new XMLHttpRequest();
    xml.onreadystatechange = function() { 
        if (xml.readyState == 4 && xml.status == 200)
            callback(body, posting);
    }
    xml.open("GET", body, true);
    xml.send(null);
}

function draw_table(map, postings){
	var img = document.createElement('img');
	console.log(map);
	img.src = map;
	lis = document.querySelector("#results");
	tr=document.createElement("tr");
	td=document.createElement("td");
	tr.appendChild(td);
	tr.appendChild(img);
	lis.appendChild(tr);
	for(var i=0; i<postings.length; i++){
		tr=document.createElement("tr");
		td=document.createElement("td");
		td2=document.createElement("td");
		price=document.createElement("td");
		td3=document.createElement("td");
		var a = document.createElement("a");
		a.href = postings[i]["external_url"];
		a.innerHTML="Link";
		td.innerHTML="Pin #: "+i.toString(10);
		td2.innerHTML=postings[i]["heading"];
		price.innerHTML="Price: $"+postings[i]["price"];
		td3.appendChild(a);
		tr.appendChild(td);
		tr.appendChild(td2);
		tr.appendChild(price);
		tr.appendChild(td3);
		lis.appendChild(tr);
	}
}