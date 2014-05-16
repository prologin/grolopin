# -*- coding: utf-8 -*-
import re, random, time, os, zipfile, Image, subprocess
from itertools import combinations

from flask import *

AFFICHE = 'prologin.png'
RESULT = 'static/img/map2.png'

RE_NAME = re.compile('^[a-z0-9]+$')
RE_MAIL = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$", re.I)

LEVELS = [3, 4, 6, 9, 28]
NB_POSITIONS_MAX = {3: 7, 4: 13, 6: 31, 9: 73, 28: 757}

LIMITS = [i*42 for i in range(1,5)]

EXOS = [
	u'<h1>GATE OF STEINER</h1><p>Vous possédez un jeu de pin\'s. Vérifier que 2 pin\'s ont toujours exactement un trou en commun.</p>',
	u'<h1>Cambriolage</h1><p>Vous possédez un jeu de clés passe-partout. Ayant minutieusement préparé le cambriolage de cette nuit, vous connaissez déjà les caractéristiques des serrures auxquelles vous allez vous attaquer (ancienneté et niveau de sécurité) et les limites de vos passe-partout : un passe-partout est dit de force (xi, yi) s\'il peut ouvrir les serrures datées d\'avant 1990 de sécurité au plus xi et les serrures datées de 1990 ou après de sécurité au plus yi.</p><p>Vous savez, de votre longue expérience de cambrioleur professionnel, que le temps de l\'opération est un facteur décisif : pas question donc de trimbaler toutes sortes de clés inutiles. Vous cherchez à savoir le nombre minimal de passe-partout à emporter pour pouvoir ouvrir toutes les serrures. S\'il est impossible de toutes les ouvrir avec votre ensemble de clés, retournez 0.</p>',
	u'<h1>Tour de magie</h1><p>Vous possédez un jeu de cartes contenant chacune une liste de nombres. Le jeu est accompagné d\'une notice :</p><p>Demandez à quelqu\'un de choisir un nombre entre 1 et 42, sans vous le dire.<br />Montrez-lui les cartes du jeu une à une et demandez-lui si son nombre figure dans la liste.<br />Faites la somme des premiers nombres de chaque carte où la personne a dit OUI, et donnez ce nombre à votre interlocuteur.<br />???<br />PROFIT!!!<br />Vous décidez alors de bêta-tester le jeu sur votre grand-mère.</p><p>« Mamie, choisis un nombre. Est-ce qu\'il est dans cette liste ? »</p><p>1 3 5 7 9 11 13 15 17 19 21 23 25 27 29 31 33 35 37 39 41 ? → OUI<br />2 3 6 7 10 11 14 15 18 19 22 23 26 27 30 31 34 35 38 39 42 ? → OUI<br />4 5 6 7 12 13 14 15 20 21 22 23 28 29 30 31 36 37 38 39 ? → NON<br />8 9 10 11 12 13 14 15 24 25 26 27 28 29 30 31 40 41 42 ? → OUI<br />16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 ? → OUI<br />32 33 34 35 36 37 38 39 40 41 42 ? → NON<br />« OK, alors ton nombre est le (1 + 2 + 8 + 16 =) 27 ! C\'est ça ?<br />— Ah, je ne sais plus !<br />— :( »</p><p>Mais pourquoi se limiter à 42 ? On vous demande de générer les cartes pour pouvoir effectuer le tour avec des nombres de 1 à N.</p>',
	u'<h1>ProLego™</h1>Vous possédez un jeu de N briques de dimensions (xi, yi, zi), ainsi qu\'une machine vous permettant de dupliquer des briques. Vous pouvez orienter les briques comme bon vous semble, et les empiler pour former une tour de briques. Cependant, pour que la construction soit stable, vous ne pouvez poser une brique i sur une brique j que si la base de la brique du dessus est strictement incluse dans la base de la brique du dessous : elles ont respectivement des dimensions a × b et a\' × b\' telles que (a < a\' et b < b\') ou (a < b\' et b < a\'). Quelle est la hauteur de la plus grande tour que vous pouvez construire ?'
]

# SQL
USERNAME = ''
PASSWORD = ''
QUERY = ''

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

"""
Gestion des bases de données
"""
def load(bdd):
	if not os.path.exists(bdd + '.json'):
		save(bdd, {})
	with open(bdd + '.json', 'r') as f:
		return json.load(f)

def save(bdd, data):
	pass # On a dit que le concours était terminé
	"""with open(bdd + '.json', 'w') as f:
		f.write(json.dumps(data))"""

def retrieve_birthyear(mail):
	p = subprocess.Popen(['mysql', '-u', 'prologin', '-p' + PASSWORD, '-D', USERNAME, '-e', QUERY % mail, '-Bs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, error = p.communicate()
	if not out:
		return 0
	else:
		return int(out.decode('latin1').split('\t')[3])

"""
Gestion des pin's
"""
def validate(pins):
	holes = []
	pins = pins.split('\n')
	if not pins[-1]: # Last line is blank
		pins = pins[:-1]
	for pin in pins:
		holes.append([m.start() for m in re.finditer('o', pin)])
	nbHoles = list(map(len, holes))
	if(nbHoles.count(nbHoles[0]) != len(nbHoles) or nbHoles[0] not in LEVELS):
		return None
	if max(map(len, pins)) > NB_POSITIONS_MAX[nbHoles[0]]:
		return None
	for a, b in combinations(holes, 2):
		if len(set(a) & set(b)) != 1:
			return None
	return (len(pins), LEVELS.index(nbHoles[0]))

"""
Gestion des parts
"""
def giveShare(ident, p, k, email=''):
	global shares, stats, affiche, pixels
	
	if not ident in stats:
		stats[ident] = {
			'owned' : [0, 0, 0, 0],
			'discover' : [0, 0, 0, 0],
			'pins' : [0, 0, 0, 0, 0]
		}
	# if not k in stats[ident]['pins']:
	#	stats[ident]['pins'][k] = 0
	
	new_pins = 0
	if p > stats[ident]['pins'][k]:
		new_pins = p - stats[ident]['pins'][k]
		stats[ident]['pins'][k] = p
		stats[ident]['lastsub'] = time.time()
	
	p = float(p) - 1
	l = float(LEVELS[k]) - 1
	n = int(16 * p * p / (l*l))
	
	if k == 4:
		added = 0
		if is_eligible(email):
			im1 = Image.open(AFFICHE)
			im2 = Image.open(RESULT)
			data1 = im1.getdata()
			data2 = list(im2.getdata())
			png_info = im2.info
			added = min(int(new_pins * 42), len(pixels))
			random.seed(42)
			for x in pixels[:added]:
				data2[x] = data1[x]
			im2.putdata(data2)
			im2.save(RESULT, **png_info)
			del im1
			del im2
			pixels = pixels[added:]
			with open('pixels', 'w') as f:
				f.write('\n'.join([str(_) for _ in pixels]))
		save('stats', stats)
		return added

	pollShares = filter(lambda x : int(lopins[x]['type']) == k, range(len(lopins)))
	
	random.seed(ident)
	random.shuffle(pollShares)
	
	added = 0
	for s in pollShares[:n]:
		share = str(s)
		if not share in shares:
			stats[ident]['owned'][k] += 1
			shares[share] = lopins[s]
			shares[share]['finder'] = []
		if not ident in shares[share]['finder']:
			added += 1
			stats[ident]['discover'][k] += 1
			if len(shares[share]['finder']) == 0:
				print(time.time(), "discover", ident, shares[share]['x'], shares[share]['y'])
			else:
				print(time.time(), "rediscover", ident, shares[share]['x'], shares[share]['y'])
			shares[share]['finder'].append(ident)
	
	save('shares', shares)
	save('stats', stats)
	
	return added

def authorizedExo(ident):
	global stats
	
	if not ident in stats:
		return []
	sizes = stats[ident]['discover']
	
	return [ i for i in range(4) if sizes[i] >= LIMITS[i]]

def is_eligible(email):
	exceptions = open('exceptions').read().split('\n')
	return retrieve_birthyear(email) >= 1992 or email in exceptions

"""
Gestion des utilisateurs
"""
def register(ip, name, email):
	global users
	
	if ip in users: return False
	
	emails = [users[x]['email'] for x in users if users[x]['name'] == name]
	
	if emails and emails[0] != email: return False
	
	users[ip] = {'name': name, 'email': email}
	
	save('users', users)
	
	print(time.time(), "register", name, email)
	
	return True

def getName(ip):
	global users
	try:
		return (users[ip]['name'], users[ip]['email'])
	except KeyError:
		return ("", "")

"""
Ajax
"""
@app.route('/name', methods=['POST', 'GET'])
def name():
	names = getName(request.headers.get("X-Forwarded-For"))
	data = "{name} {email}".format(name=names[0], email=names[1])
	return Response(data, mimetype='text/plain')


@app.route('/register', methods=['POST', 'GET'])
def _register():
	name = request.args.get("name", "").lower()
	email = request.args.get("email", "").lower()
	ip = request.headers.get("X-Forwarded-For")
	
	if RE_NAME.search(name) is None: return Response('1', mimetype='text/plain')
	if RE_MAIL.search(email) is None: return Response('2', mimetype='text/plain')
	if register(ip, name, email) is False: return Response('3', mimetype='text/plain')
	
	return Response('0', mimetype='text/plain')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
	soum = request.args.get("submit", "")
	ident = getName(request.headers.get("X-Forwarded-For"))[0]
	if not ident:
		return Response('-2', mimetype='text/plain')
	values = validate(soum)
	print(time.time(), "validate", ident, soum.replace('\n', '\\n'))
	if soum and values:
		n = giveShare(ident, values[0], values[1])
		return Response(str(n), mimetype='text/plain')
	return Response('-1', mimetype='text/plain')

@app.route('/submit2', methods=['POST', 'GET'])
def submit2():
	if request.method == 'POST':
		f = request.files['pins']
		if f:
			z = zipfile.ZipFile(f)
			if 'pins.txt' in z.namelist():
				soum = z.read('pins.txt')
				ident, email = getName(request.headers.get("X-Forwarded-For"))
				if not ident:
					return Response('-2', mimetype='text/plain')
				values = validate(soum)
				print(time.time(), "validate", ident, 'FOREIGN ESTATE')
				if soum and values:
					n = giveShare(ident, values[0], values[1], email)
					return Response(str(n), mimetype='text/plain')
	return Response('-1', mimetype='text/plain')

@app.route('/data', methods=['POST', 'GET'])
def _data():
	with open("shares.json", 'r') as f:
		m = "lopins = " + f.read() + ";\n"
	with open("stats.json", 'r') as f:
		m += "stats = " + f.read() + ";\n"
	m += "me = '" + getName(request.headers.get("X-Forwarded-For"))[0] + "';\n"
	return Response(m, mimetype='text/javascript')

"""
Pages Web
"""
@app.route('/surprise', methods=['POST', 'GET'])
def surprise():
	try:
		exo = int(request.args.get("num", ""))
	except ValueError:
		exo = 0
	if exo  in authorizedExo(getName(request.headers.get("X-Forwarded-For"))[0]):
		return Response(render_template('exos.html', enonce=EXOS[exo]))
	else:
		return Response(render_template('exos.html', enonce=u"Vous n'avez pas accès à la surprise."))

def datetimeformat(value):
	return time.ctime(-value)

@app.route('/classement', methods=['POST', 'GET'])
def classement():
	classement = sorted(map(lambda x : (x[0], (sum(x[1]['pins']), -x[1]['lastsub'])),stats.items()), key=lambda x : x[1], reverse=True)
	app.jinja_env.filters['datetimeformat'] = datetimeformat
	return Response(render_template('classement.html', classement=classement))

@app.route('/map', methods=['POST', 'GET'])
def _map():
	exos = authorizedExo(getName(request.headers.get("X-Forwarded-For"))[0])
	available = [i in exos for i in range(4)]
	colors = ["#ff9", "#fc0", "#f90", "#d60"]
	return Response(render_template('map.html', sizes=LIMITS, available=available, colors=colors))

@app.route('/map2', methods=['POST', 'GET'])
def _map2():
	email = getName(request.headers.get("X-Forwarded-For"))[1]
	return Response(render_template('map2.html', eligibility=u'Vous êtes éligible.' if email and is_eligible(email) else u'Vous n\'êtes pas éligible.' or email in exceptions, now=time.time()))

@app.route('/pins', methods=['POST', 'GET'])
def pins():
	return Response(render_template('pins.html'))

@app.route('/', methods=['POST', 'GET'])
def howto():
	return Response(render_template('howto.html'))

"""
Run
"""
if __name__ == '__main__':
	with open('pixels') as f:
		pixels = [int(_) for _ in f.read().splitlines()]

	lopins = load('lopins')
	stats = load('stats')
	users = load('users')
	shares = load('shares')
	app.run(host='localhost', port=5000)
