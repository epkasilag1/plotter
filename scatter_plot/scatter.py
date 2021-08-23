import matplotlib.pyplot as plt
from vincenty import vincenty

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

f = open('C:/EQP11-20/Programs/PLOT.OUT')
lines = f.readlines()
f.close()

epi_lat = float(lines[2][6:13])
epi_lon = float(lines[2][14:22])
epicenter = (epi_lat, epi_lon)
print (epicenter)
epi_depth = float(lines[2][22:29])
print (epi_depth)
epi_mag = float(input('Enter magnitude: '))

f = open('quakes.txt')
lines = f.readlines()
f.close()

lat = []
lon = []
dep = []
size = []

for line in lines:
	year = int(line[0:4])
	if (year >= 2010):
		latitude = float(line[6:12])
		longitude = float(line[14:21])
		depth = int(line[23:26])
		magnitude = float(line[28:31])
		delt, azim = vincenty(epicenter, (latitude, longitude))
		if (delt * 111.19 <= 200):
			lat.append(latitude)
			lon.append(longitude)
			dep.append(depth)
			size.append(2*2**magnitude)
		# lat.append(latitude)
		# lon.append(longitude)
		# dep.append(depth)
		# size.append(2*2**magnitude)

ax.scatter(lat, lon, dep, c='gray', marker='o', s=size)
ax.scatter([epicenter[0]], [epicenter[1]], [epi_depth], c='red', marker='o', s=[2*2**epi_mag])

ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Depth')

ax.invert_zaxis()

plt.savefig('3dscatter.pdf', format='pdf')
plt.show()