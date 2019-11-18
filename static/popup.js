async function get_def(word, key, callback){
	uri= "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"+word+"?key="+key;
	let opts = {
		method: 'GET',
	}
	let resp = await fetch(uri, opts);
	result = await resp.json();
	callback(result);
}

function popup(results){
	var modal = document.getElementById("myModal");
	modal.style.display = "block";
	var def=results[0]["shortdef"]
	for(var i=1; i<results.length; i++){
		def = def +","+(results[i]["shortdef"])
	}
	def.replace(",",", ")
	modal.innerHTML=def;
}

window.onclick = function(event) {
	var modal = document.getElementById("myModal");
	if (event.target == modal) {
		modal.style.display = "none";
	}
}