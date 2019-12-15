function draw_table(maps, titles, descs){
	section = document.querySelector("#section");
	lis = document.querySelector("#results");
	res.removeChild(res.childNodes[0])
	
	for(var i=0; i<maps.length; i++){	
		map=maps[i];
		var img = document.createElement('img');
		img.src = map;
		tr=document.createElement("tr");
		td=document.createElement("td");
		td2=document.createElement("td");
		td3=document.createElement("td");
		t_body=document.createElement("tbody");
		
		td.innerHTML=titles[i];
		td2.innerHTML=descs[i];
		td3.appendChild(img);
		
		tr.appendChild(td);
		tr.appendChild(td2);
		tr.appendChild(td3);
		lis.appendChild(tr);
		t_body.appendChild(lis);
	}
}