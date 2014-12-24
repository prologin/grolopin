var currentPinsId;
var currentTypeAlert;
var DIFFERENT_NB_HOLES = 0
var INCORRECT_NB_HOLES = 1
var TOO_LONG = 2
var TWO_COMMON_HOLES = 3
var ZERO_COMMON_HOLES = 4
var UNKNOWN_CHARACTER = 5

var name = null
var email = null

function init()
{
	login()
}

function login()
{
	jQuery.ajax({
		type: 'GET',
		url: '/name',
		success: function(data, textStatus, jqXHR) {
			data = data.split(" ")
			name = data[0]
			email = data[1]
			update('')
		},
		});
}

function register(name, email)
{
	jQuery.ajax({
		type: 'GET',
		url: '/register',
		data: {
			'name': name,
			'email':email
		},
		success: function(data, textStatus, jqXHR) {
			switch (data)
			{
			case '0':
				update("Enregistrement effectué", true)
				login()
			break
			case '1':
				update("Erreur dans le pseudo", true)
			break
			case '2':
				update("Erreur dans l'email", true)
			break
			case '3':
				update("Le pseudo a déjà été utilisé", true)
			break
			}
		},
		});
}

function update(msg, ok)
{
	if (msg)
	{
		if (ok)
			cl = 'alert alert-success'
		else
			cl = 'alert alert-error'
		$('#comment').html(msg).attr('class', cl)
	}
	if (name)
	{
		$('#register').hide()
		$('#_pseudo').html('Hi <strong>' + name + '</strong>!')
		$('#_pseudo').show()
		$('#_register').show()
	}
	else
	{
		$('#register').show()
		$('#_register').hide()
	}
}

function subPins(data)
{
	jQuery.ajax({
		type: 'GET',
		url: '/submit',
		data: {'submit': data},
		success: function(data, textStatus, jqXHR) {
			if (data == '-2')
				update("Ce jeu de pin's est correct.", true);
			else if (data == '-1')
				update("Le jeu de pin's envoyé est incorrect.", false);
			else if (data == '0')
				update("Vous n'avez rien débloqué.", true);
			else
				update("Bravo, vous avez débloqué " + data + " lopins. <a href='/map'>Voir la carte.</a>", true);
		}
		});
}

function tryPins(data) {
	var pins = data.split('\n')
	var nonEmptyPins = []
	for(var i = 0 ; i < pins.length ; i++) {
		if(pins[i].length > 0)
			nonEmptyPins.push(pins[i])
	}
	pins = nonEmptyPins
	$('#pins').attr('value', pins.join('\n'))
	$('#pinslist').empty().css('display', 'inline-block')
	$.each(pins, function(i, pin) { $('#pinslist').append($('<span>').attr({
		'id': 'pin' + i,
		'onmouseover': 'displayPins([' + i + ', -1])',
		'onmouseout': 'alertPins(currentPinsId, currentTypeAlert)'
	}).html(pin)) })
	var nbTrous = new Array(pins.length)
	var nbPositions = 0
	var iPosMax
	for(var i = 0 ; i < pins.length ; i++) {
		nbTrous[i] = 0
		if(pins[i].length > nbPositions) {
			nbPositions = pins[i].length
			iPosMax = i
		}
		for(k = 0 ; k < pins[i].length ; k++) {
			if(pins[i][k] == 'o')
				nbTrous[i]++
			else if(pins[i][k] != ' ' && pins[i][k] != '.')
				return alertPins([], UNKNOWN_CHARACTER)
		}
		if(nbTrous[i] != nbTrous[0])
			return alertPins([0, i], DIFFERENT_NB_HOLES)
	}
	if([3, 4, 6, 9].indexOf(nbTrous[0]) == -1)
		return alertPins([0], INCORRECT_NB_HOLES)
	nbPositionsMax = {3: 7, 4: 13, 6: 31, 9: 73};
	if(nbPositions > nbPositionsMax[nbTrous[0]])
		return alertPins([iPosMax], TOO_LONG, nbPositionsMax[nbTrous[0]]);
	for(var i = 0 ; i < pins.length ; i++)
		for(var j = i + 1 ; j < pins.length ; j++) {
			var aTrou = false
			for(var k = 0 ; k < Math.min(pins[i].length, pins[j].length) ; k++)
				if(pins[i][k] == 'o' && pins[j][k] == 'o') {
					if(aTrou)
						return alertPins([i, j], TWO_COMMON_HOLES)
					aTrou = true
				}
			if(!aTrou)
				return alertPins([i, j], ZERO_COMMON_HOLES)
		}
	update('Ce jeu de pin\'s est correct. Soumission en cours…', true)
	currentPinsId = undefined
	currentTypeAlert = undefined
	subPins($('#pins').attr('value'))
}

function alertPins(pinsId, typeAlert, arg) {
	if(pinsId == undefined || typeAlert == undefined)
		return
	currentPinsId = pinsId
	currentTypeAlert = typeAlert
	$.each(pinsId, function(i, pinId) { $('#pin' + pinId).addClass('active') });
	var message
	switch(typeAlert) {
		case DIFFERENT_NB_HOLES: message = 'Ces pin\'s n\'ont pas le même nombre de trous.'; displayPins(); break
		case INCORRECT_NB_HOLES: message = 'Vos pin\'s n\'ont pas 3, 4, 6 ou 9 trous.'; displayPins(); break
		case TOO_LONG: message = 'Ce pin\'s est trop long, l\'engrenage ne comporte que ' + arg + ' dents.'; displayPins(); break
		case TWO_COMMON_HOLES: message = 'Ces pin\'s ont plus d\'un trou en commun.'; displayPins(pinsId); break
		case ZERO_COMMON_HOLES: message = 'Ces pin\'s n\'ont pas de trou en commun.'; displayPins(pinsId); break
		case UNKNOWN_CHARACTER: message = 'Les seuls caractères possibles sont « o », l\'espace et éventuellement le point.'; displayPins(); break
	}
	update(message, false);
}

function hasHole(pin, k) {
	return pin != undefined && k < pin.length && pin[k] == 'o'
}

function displayPins(pinsId) {
	var c = document.getElementById('preview').getContext('2d')
	c.clearRect(0, 0, c.canvas.width, c.canvas.height)
	if(pinsId == undefined)
		return;
	pins = $('#pins').attr('value').split('\n')
	nbPositions = 0
	for(var i = 0 ; i < pins.length ; i++)
		if(pins[i].length > nbPositions)
			nbPositions = pins[i].length
	switch(nbPositions) {
		case 3: dalpha = 0.330; break
		case 7: dalpha = 0.229; break
		case 13: dalpha = 0.118; break
		default: dalpha = 0.300;
	}
	$('#preview').css('background', 'url(/static/img/pins' + ((nbPositions == 7 || nbPositions == 13) ? nbPositions : 0) + '.png) no-repeat')
	c.lineWidth = 1
	c.strokeStyle = '#000'
	for(var k = 0 ; k < nbPositions ; k++) {
		c.beginPath()
		c.fillStyle = '#000'
		alpha = 2 * k * Math.PI / nbPositions + dalpha
		c.arc(149 + 67 * Math.cos(alpha), 121 - 67 * Math.sin(alpha), 4, 0, 2 * Math.PI, true)
		if(hasHole(pins[pinsId[0]], k) && hasHole(pins[pinsId[1]], k))
			c.fillStyle = '#f99'
		if(hasHole(pins[pinsId[1]], k))
			c.fill()
		if(hasHole(pins[pinsId[0]], k) || hasHole(pins[pinsId[1]], k))
			c.stroke()
	}
}
