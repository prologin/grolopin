import sys, Image, json

SIZE = 10
ZONE = [(0, 0, 0, 255), (255, 255, 0, 255), (255, 0, 0, 255), (0, 255, 0, 255)]
LEVEL = [3, 2, 1, 0]
number = [0, 0, 0, 0]

def lopin(x, y):
	for i in range(0, SIZE):
		for j in range(0, SIZE):
			yield (i + x * SIZE, j + y * SIZE)

im = Image.open(sys.argv[1]) 
data = list(im.getdata())

lopins = []

ndata = [(0, 0, 255, 255)] * (len(data) / (SIZE*SIZE))

for x in range(im.size[0] / SIZE):
	for y in range(im.size[1] / SIZE):
		for i in range(len(ZONE)):
			if ZONE[i] in map(lambda x : data[x[0] + x[1] * im.size[0]], lopin(x, y)):
				lopins.append({'x' : x, 'y' : y, 'type' : LEVEL[i], 'finder' : []})
				ndata[x + y * im.size[0]/SIZE] = ZONE[i]
				number[LEVEL[i]] += 1
				break
			

imNew=Image.new(im.mode , (im.size[0]/SIZE, im.size[1]/SIZE))
imNew.putdata(ndata)
imNew.save("test.png")

with open("lopins.json", 'w') as f:
	f.write(json.dumps(lopins))

print(number)

