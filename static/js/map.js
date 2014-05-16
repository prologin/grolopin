var me = null;
var selectedPlayer = null;
var lopins = null;
var stats = null;

var done = 0;

var grolopin = null;
var owners = {};

var save = null;

SIZE = 10

var imageLopin = new Image()
imageLopin.onload = function(){updateServ()}

function paintLopin(x, y, col, borderCol) {
	map = grolopin.getContext('2d')
	map.beginPath()
	map.moveTo(x * SIZE, y * SIZE)
	map.lineTo((x + 1) * SIZE, y * SIZE)
	map.lineTo((x + 1) * SIZE, (y + 1) * SIZE)
	map.lineTo(x * SIZE, (y + 1) * SIZE)
	map.closePath()
	if(col) {
		map.fillStyle = col
		map.fill()
	}
	
	if(borderCol) {
		map.strokeStyle = borderCol
		map.stroke()
	}
}

function init() {
	grolopin = document.getElementById('grolopin')
	imageLopin.src = '/static/img/lopins.png'
	setInterval("updateServ()", 10000)
}

function updateServ() {
	jQuery.ajax({
		type: 'GET',
		url: '/data',
		success: function(data, textStatus, jqXHR) {eval(data);update();$('#grolopin').css("background", "url('/static/img/map.png') no-repeat");$('body').css("background", "#cef");  }});
}

function update() {
	map = grolopin.getContext('2d')
	
	map.clearRect(0, 0, grolopin.width, grolopin.height)
	
	for(var i in lopins)
	{
		var lopin = lopins[i]
		owners[lopin.y * grolopin.width / SIZE + lopin.x] = lopin.finder[0]
		map.drawImage(imageLopin, SIZE*lopin.type, 0, SIZE, SIZE,  lopin.x*SIZE, lopin.y*SIZE, SIZE, SIZE)
		// console.log(lopin.x*SIZE, lopin.y*SIZE, SIZE, SIZE, SIZE*lopin.type, 0, SIZE, SIZE)
	}
	
	for(var i in lopins)
	{
		var lopin = lopins[i]
		
		if  (lopins[i].finder.indexOf(selectedPlayer) >= 0)
		{
			if(lopin.finder[0] == selectedPlayer)
				border = '#f00'
			else
				border = '#000'
			paintLopin(lopin.x, lopin.y, null, border)
		}
	}
	
	if (stats[me] != undefined)
		nbLopins = stats[me]['discover']
	else
		nbLopins = [0, 0, 0, 0]
	//Affichage nombre lopins
	for(var i = 0 ; i < 4 ; i++)
		$('#nb' + i).html(nbLopins[i])
	
	save = grolopin.getContext('2d').getImageData(0,0, grolopin.width, grolopin.height)
	
	done = 1
	if(selectedPlayer == null) // Pour éviter un truc vraiment dégueulasse
		updateRanking()
}

function updateRanking() {
	players = []
	$('#ranking').html('');
	for(player in stats)
		players.push(player)
	players.sort(function(i, j) {
		u = stats[i]
		v = stats[j]
		return (v.owned[0] + v.owned[1] + v.owned[2] + v.owned[3]) - (u.owned[0] + u.owned[1] + u.owned[2] + u.owned[3])
	})
	for(var i = 0 ; i < players.length ; i++) {
		var u = stats[players[i]]
		var o = u.owned[0] + u.owned[1] + u.owned[2] + u.owned[3]
		var k = u.discover[0] + u.discover[1] + u.discover[2] + u.discover[3]
		$('#ranking').append('<tr><td><a onmouseover="javascript:selectedPlayer = \'' + players[i] + '\'; updateServ()" onmouseout="javascript:selectedPlayer = null; updateServ()">' + players[i] + '</a></td><td>' + o + '</td><td>' + k + '</td></tr>')
	}
}

ix = undefined
iy = undefined
function move(mx, my) {
	if (done == 0)
		return
	
	bound = grolopin.getBoundingClientRect()
	var x = Math.floor((mx - bound.left) / SIZE)
	var y = Math.floor((my - bound.top) / SIZE)
	
	map = grolopin.getContext('2d')
	
	map.clearRect(0, 0, grolopin.width, grolopin.height)
	map.putImageData(save,0,0)
	
	if(owners.hasOwnProperty(y * grolopin.width / SIZE + x))
	{
		ix = x
		iy = y
		map.font = '10px Arial'
		map.textBaseline = 'bottom'
		map.textAlign = 'center'
		if (owners[y * grolopin.width / SIZE + x] == me)
			map.fillStyle = '#f00'
		else
			map.fillStyle = '#fff'
		map.fillText(owners[y * grolopin.width / SIZE + x], mx - bound.left, my - bound.top - 5)
		paintLopin(x, y, '#f00')
	} else if(ix != undefined) {
		ix = undefined
		iy = undefined
	}
}
