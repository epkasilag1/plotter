import re, io

class Earthquake:
	def __init__(self, year, latitude, longitude, magnitude, depth):
		self.year = year
		self.latitude = latitude
		self.longitude = longitude
		self.magnitude = magnitude
		self.depth = depth

quakes = []

f = io.open('epicsort.tmp', 'r', encoding='ISO-8859-1')
lines = f.readlines()
f.close()

for line in lines:
	lat = float(line[27:34])
	lon = float(line[34:41])
	year = int(line[6:10])

	if (re.search('[0-9]', line[41:44])):
		depth = int(line[41:44])
	else:
		depth = None

	if (re.search('[1-9].[0-9]', line[58:61])):
		magnitude = float(line[58:61])
	elif (re.search('[1-9].[0-9]', line[53:56])):
		magnitude = float(line[53:56])
	elif (re.search('[1-9].[0-9]', line[49:52])):
		magnitude = float(line[49:52])
	else:
		magnitude = None

	if (magnitude != None and depth != None):
		q = Earthquake(year=year, latitude=lat, longitude=lon, depth=depth, magnitude=magnitude)
		quakes.append(q)

f = open('quakes.txt', 'w')
for q in quakes:
	f.write(str(q.year).rjust(4) + str(q.latitude).rjust(8) + str(q.longitude).rjust(9) + str(q.depth).rjust(5) + str(q.magnitude).rjust(5) + '\n')
f.close()