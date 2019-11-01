//Function: gets the user's current location
function get_loc() {
  //Fetches max search area
  var radius = document.querySelector("#max");
  if(radius.value>50 || radius.value<=0){
	  alert("Your search area is out of bounds. Must be less than 50 Miles and positive.")
	  return;}
  //Deletes current table/image on screen (if needed)
  var old = document.querySelector("#results");
  var newtable = document.createElement('tbody');
  newtable.id="results";
  var old_img = document.querySelector("img");
  if(old_img){
	  old_img.parentNode.removeChild(old_img);
  }
  old.parentNode.replaceChild(newtable, old);
  //Gets users location
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(extract);
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}
//Function: extracts lat and long from position
function extract(position){
  var lat = position.coords.latitude;
  var lon = position.coords.longitude;
  get_postings(lat, lon, "http://search.3taps.com/", get_map);
}
//Function: Gets the first page of postings from 3 taps
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
//Function: Gets the rest of the pages of postings
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
//Function: Fetches all the maps needed to draw returned postings
async function get_map(postings, lat, lon, callback){
	var posting = postings["postings"];
	if(posting.length==0){
		alert("Bad news! No local postings of your search!");
		return;
	}
	if(postings["num_matches"]>50){alert('Lots of results! Will take a little while to load.');}
	//Uses get_more_postings to fetch all postings
	while(postings["next_page"]!=-1){
		let temp = await get_more_postings(lat, lon, postings["next_page"]);
		posting = posting.concat(temp["postings"]);
		postings["next_page"]=temp["next_page"];
	}
	//Splits the posting list into batches of 20 (because thats how they are mapped)
	var batch=[]
	window.batch_posts=[];
	for(var i=0; i<posting.length; i++){
		if((i+1)%20==0){
			batch.push(posting[i]);
			window.batch_posts.push(batch);
			batch=[];
		}
		else{
			batch.push(posting[i]);
		}
	}
	if(window.batch_posts[-1]!=batch){
		window.batch_posts.push(batch);
	}
	//Creates list of links to the map images
	var maps = [];
	for(var i=0; i<window.batch_posts.length; i++){	
		var body="https://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels?pp="+lat+","+lon+";0;YOU";
		var start = 0;
		var current_batch = window.batch_posts[i];
		
		for(var j=0; j<current_batch.length; j++){
			if(j==current_batch.length-1){
				if(j==start){
					body+="&pp="+current_batch[j]["location"]["lat"]+","+current_batch[j]["location"]["long"]+";4;"+(j+1);
					start=j+1;
				}
				else{
					var start_j = (start+1).toString()+"-"+(j+1).toString();
					body+="&pp="+current_batch[j]["location"]["lat"]+","+current_batch[j]["location"]["long"]+";4;"+start_j;
					start=j+1;
				}	
			}
			else if(current_batch[j]["location"]["lat"]!=current_batch[j+1]["location"]["lat"] ||
			current_batch[j]["location"]["long"]!=current_batch[j+1]["location"]["long"]){
				if(j==start){
					body+="&pp="+current_batch[j]["location"]["lat"]+","+current_batch[j]["location"]["long"]+";4;"+(j+1);
					start=j+1;
				}
				else{
					var start_j = (start+1).toString()+"-"+(j+1).toString();
					body+="&pp="+current_batch[j]["location"]["lat"]+","+current_batch[j]["location"]["long"]+";4;"+start_j;
					start=j+1;
				}
			}
		}
		body+="&key=AvWjYu-PKLX_yA_wjaiVhhgn8L4zISfT_zN1cpFjwLyzByKro4crRk6pOE1r8fmI";
		body = body.split('%').join('');
		maps.push(body);
	}
	callback(maps, window.batch_posts);
}
//Funtion: Draws table for the first map (which shows the first 20 closest postings)
function draw_table(maps){
	map=maps[0];
	window.maps=maps;
	window.index=0;
	current_batch=window.batch_posts[0];
	
	var img = document.createElement('img');
	img.src = map;
	section = document.querySelector("#section");
	section.appendChild(img);
	lis = document.querySelector("#results");
	
	if(window.index<window.batch_posts.length-1){
		var next = document.createElement('button');
		next.onclick=next_results;
		next.innerHTML="Show more results";
	
		var button_row = document.createElement("tr");
		var next_cell = document.createElement("td");
		next_cell.className="half_table";
		
		next_cell.appendChild(next);
		button_row.appendChild(next_cell);
	}
	for(var i=0; i<current_batch.length; i++){	
		tr=document.createElement("tr");
		td=document.createElement("td");
		td2=document.createElement("td");
		price=document.createElement("td");
		td3=document.createElement("td");
		var a = document.createElement("a");
		a.href = current_batch[i]["external_url"];
		a.innerHTML="Link";
		td.innerHTML="Pin #: "+i.toString();
		td2.innerHTML=current_batch[i]["heading"];
		price.innerHTML="Price: $"+current_batch[i]["price"];
		td3.appendChild(a);
		tr.appendChild(td);
		tr.appendChild(td2);
		tr.appendChild(price);
		tr.appendChild(td3);
		lis.appendChild(tr);
	}
	lis.appendChild(button_row);
}
//Funtion: Draws table and map for next 20 results
function next_results(){
	window.index+=1;
	var old = document.querySelector("#results");
	var newtable = document.createElement('tbody');
	newtable.id="results";
	old.parentNode.replaceChild(newtable, old);
	
	map=window.maps[window.index];
	current_batch=window.batch_posts[window.index];
	
	var img = document.querySelector('img');
	img.src = map;
	lis = document.querySelector("#results");
	
	if(window.index<window.batch_posts.length-1){
		var next = document.createElement('button');
		next.onclick=next_results;
		next.innerHTML="Show next results";
	}
	
	var prev = document.createElement('button');
	prev.onclick=prev_results;
	prev.innerHTML="Show previous results";
	
	var button_row = document.createElement("tr");
	var prev_cell = document.createElement("td");
	var space1=document.createElement("td");
	var space2=document.createElement("td");
	space1.className="no_outline";
	space2.className="no_outline";
	var next_cell = document.createElement("td");
	prev_cell.className="half_table";
	next_cell.className="half_table";
	
	prev_cell.appendChild(prev);
	button_row.appendChild(prev_cell);
	if(window.index<window.batch_posts.length-1){
		next_cell.appendChild(next);
		button_row.appendChild(space1);
		button_row.appendChild(space2);
		button_row.appendChild(next_cell);
	}
	
	for(var i=0; i<current_batch.length; i++){
		
		tr=document.createElement("tr");
		td=document.createElement("td");
		td2=document.createElement("td");
		price=document.createElement("td");
		td3=document.createElement("td");
		var a = document.createElement("a");
		a.href = current_batch[i]["external_url"];
		a.innerHTML="Link";
		
		td.innerHTML="Pin #: "+(i+1).toString();
		td2.innerHTML=current_batch[i]["heading"];
		price.innerHTML="Price: $"+current_batch[i]["price"];
		td3.appendChild(a);
		tr.appendChild(td);
		tr.appendChild(td2);
		tr.appendChild(price);
		tr.appendChild(td3);
		lis.appendChild(tr);
	}
	lis.appendChild(button_row);
}
//Funtion: Draws table and map for previous 20 results
function prev_results(){
	window.index-=1;
	var old = document.querySelector("#results");
	var newtable = document.createElement('tbody');
	newtable.id="results";
	old.parentNode.replaceChild(newtable, old);
	
	map=window.maps[window.index];
	current_batch=window.batch_posts[window.index];
	
	var img = document.querySelector('img');
	img.src = map;
	lis = document.querySelector("#results");
	
	var next = document.createElement('button');
	next.onclick=next_results;
	next.innerHTML="Show next results";
	
	if(window.index>0){
		var prev = document.createElement('button');
		prev.onclick=prev_results;
		prev.innerHTML="Show previous results";
	}
	
	var button_row = document.createElement("tr");
	var prev_cell = document.createElement("td");
	var space1=document.createElement("td");
	var space2=document.createElement("td");
	space1.className="no_outline";
	space2.className="no_outline";
	var next_cell = document.createElement("td");
	prev_cell.className="half_table";
	next_cell.className="half_table";
	
	next_cell.appendChild(next);
	if(window.index>0){
		prev_cell.appendChild(prev);
		button_row.appendChild(prev_cell);
		button_row.appendChild(space1);
		button_row.appendChild(space2);
	}
	button_row.appendChild(next_cell);
	
	for(var i=0; i<current_batch.length; i++){
		
		tr=document.createElement("tr");
		td=document.createElement("td");
		td2=document.createElement("td");
		price=document.createElement("td");
		td3=document.createElement("td");
		var a = document.createElement("a");
		a.href = current_batch[i]["external_url"];
		a.innerHTML="Link";
		
		td.innerHTML="Pin #: "+(i+1).toString();
		td2.innerHTML=current_batch[i]["heading"];
		price.innerHTML="Price: $"+current_batch[i]["price"];
		td3.appendChild(a);
		tr.appendChild(td);
		tr.appendChild(td2);
		tr.appendChild(price);
		tr.appendChild(td3);
		lis.appendChild(tr);
	}
	lis.appendChild(button_row);
}