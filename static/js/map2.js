$(document).ready(function () {
	$(':button').click(function(){
		var formData = new FormData($('form')[0])
		console.log('envoi', formData)
		$.ajax({
			url: '/submit2',
			type: 'POST',
			success: function(data) {
				switch(data) {
					case '-2': update("Vous devez <a href='/pins'>vous inscrire</a> pour recevoir des lopins.", false); break
					case '-1': update("Le jeu de pin's envoyé est incorrect. Vous ne pouvez pas soumettre avant 10 minutes.", false); break
					case '0': update("Vos pin's sont corrects. Vous n'avez rien débloqué.", true); break
					default: update("Bravo, vous avez débloqué " + data + " lopins.", true);
				}
				d = new Date()
				$('#map').attr('src', '/static/img/map2.png?' + d.getTime())
			},
			error: function() { alert('Oups, ça ne semble pas avoir fonctionné.') },
			data: formData,
			cache: false,
			contentType: false,
			processData: false
		});
	});
	
	$('input[id=pins]').change(function() {
		$('#pinsCover').val($(this).val().replace('C:\\fakepath\\', ''))
	});
});

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
}