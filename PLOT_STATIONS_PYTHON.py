import pygmt, math, re, time
import numpy as np


# READ TRAVEL TIME TABLE (JBTAB.PS)
def read_table(jbtab):
	f = open(jbtab)
	lines = []
	
	for line in f:
	    line = line.strip('\n')                  #removing new line
	    line = re.sub(' +', ' ', line.lstrip())  #removing multiple spaces
	    lines.append(line)
	f.close()
	
	lc = 0
	HEADER = []
	DEP = [[] for i in range(15)]
	TTMTAB = [[[0.0 for k in range(2)] for j in range(15)] for i in range(120)]
	NUMDEP = []
	DEP1ST = []
	DDELT = []
	NUMDTA = []

	for i in range(2):
	    HEADER.append(lines[lc])
	    lc += 1
	    
	    line = lines[lc].split(' ')
	    numdep = int(line[0])
	    dep1st = float(line[1])	    
	    ddelt = float(line[2])
	    numdta = int(line[3])
	    NUMDEP.append(numdep)
	    DEP1ST.append(dep1st)
	    DDELT.append(ddelt)
	    NUMDTA.append(numdta)
	    lc += 1

	    for j in range(numdep):
	        depths = []
	        DEP[j].append(float(lines[lc]))
	        lc += 1
	        while (len(depths) != numdta):
	            line = lines[lc]
	            line = line.split(' ')
	            for d in line:
	                depths.append(float(d))
	                if (len(depths) == numdta):
	                    break
	            lc += 1
	        for k in range(len(depths)):
	        	TTMTAB[k][j][i] = depths[k]

	return TTMTAB, HEADER, NUMDEP, DEP1ST, DDELT, NUMDTA, DEP

# RETURNS STATIONS' NAMES, LONS, AND LATS (PHILSTA AND PHILSTA-MAIN)
# RETURNS STATIONS' NAMES, P AND s ARRIVALS (PLOT.DAT)
def get_station_locations(filename):
	lines = []
	f = open(filename)
	for line in f:
		line = line.strip('\n')
		lines.append(line)
	f.close()

	station_names = []
	station_latitude = []
	station_longitude = []
	P = []
	S = []
	if (filename == 'PLOT.DAT'):
		lines = lines[1:-1]
		for line in lines:
			s_name = line[0:5]
			p = line[7:14]
			s = line[17:24]
			station_names.append(s_name)
			P.append(p)
			S.append(s)
		return station_names, P, S	
		

	for line in lines:
		s_name = line[0:5]
		s_lat = float(line[7:14])
		s_lon = float(line[17:24])
		station_names.append(s_name)
		station_latitude.append(s_lat)
		station_longitude.append(s_lon)
	
	return station_names, station_latitude, station_longitude

# RETURNS EPICENTER LOCATION FROM PLOT.OUT
def epicenter_location(filename):
	lines = []
	f = open(filename)
	for line in f:
		line = line.strip('\n')
		lines.append(line)
	f.close()
	line = lines[2]
	OLAT = float(line[6:12])
	OLON = float(line[14:21])
	return OLON, OLAT

# RETURNS DEPTH FROM PLOT.OUT
def get_depth(filename):
	f = open(filename)
	lines = f.readlines()
	f.close()
	line = lines[2]
	depth = float(line[22:28])
	return depth

# IGNORE THIS
def get_bounds(var, stations_long, stations_lat):
	if (var == 'low'):
		s_long = min(stations_long)
		s_lat = min(stations_lat)
		return s_long, s_lat
	if (var == 'high'):
		s_long = max(stations_long)
		s_lat = max(stations_lat)
		return s_long, s_lat

# RETURNS RESP AND RESS FROM PLOT.OUT
def get_residual(filename, plot_sta, plot_s):
	file = open(filename)
	lines = []
	for line in file:
		line = line.strip('\n')
		lines.append(line)
		# print (line)
	file.close()

	stations = [sta[0:3] for sta in plot_sta]

	lines = lines[8:]
	resp = []
	ress = []
	# print (stations)
	for line in lines:
		sta_ = line[0:3]
		resp_ = line[30:39]
		ress_ = line[39:48]
		resp.append(float(resp_))
		# print (ress)
		
		# print (sta_)
		if (sta_ in stations and plot_s[stations.index(sta_)] != '       '):
			ress.append(float(ress_))
	return resp, ress

# RETURNS STATIONS' DETAILS FROM PLOT.OUT
def get_solution(filename):
	file = open(filename)
	lines = []
	for line in file:
		line = line.strip('\n')
		lines.append(line)
		# print (line)
	file.close()

	lines = lines[8:]
	sta = []
	toa = []
	azim = []
	delta = []
	resp = []
	ress = []
	obsp = []
	obss = []
	calcp = []
	calcs = []
	for line in lines:
		sta.append(line[0:4])
		toa.append(line[4:12])
		azim.append(line[12:21])
		delta.append(line[21:30])
		resp.append(line[30:39])
		ress.append(line[39:48])
		obsp.append(line[48:57])
		obss.append(line[57:66])
		calcp.append(line[66:75])
		calcs.append(line[75:84])
	return sta, toa, azim, delta, resp, ress, obsp, obss, calcp, calcs

# RETURNS THE NUMBER OF P-ARRIVALS USED IN COMPUTATION
# RETURNS THE NUMBER OF S-ARRIVALS USED IN COMPUTATION
#	0 RESS IS TREATED AS NO S-ARRIVAL RECORDED
def ps_arrival(resp, ress):
	P = len(resp)
	S = len(ress)
	return P, S

# IGNORE THIS
# def DELAZ(slat, slon, eplat, eplon):
# 	return vincenty((eplat, eplon), (slat, slon))

# RETURNS THE NUMBER OF STATIONS THAT ARE AT MOST 200KM AWAY FROM EPICENTER
def within200(DELTA):
	D = 0
	for i in range(len(DELTA)):
		if (float(DELTA[i])*111.2 <= 200):
			D += 1
	return D


# x1 and x2 are depths from JBTAB.PS
# time1 and time2 are time tables for x1 and x2, respectively
# x is the depth of the hypocenter
# returns time table for x
def interpolate(x1, x2, time1, time2, x):
	time = []
	for i in range(len(time1)):
		y1, y2 = time1[i], time2[i]
		y = y1 + ((x - x1) / (x2 - x1)) * (y2 - y1)
		time.append(y)
	return time

# sorting azimuth in increasing order
def sort_sta_azim(sta, azim):
	sorted_sta = [s for s in sta]
	sorted_azim = [float(a) for a in azim]
	for i in range(len(azim)):
		for j in range(i, len(azim)):
			if (sorted_azim[i] > sorted_azim[j]):
				temp_sta = sorted_sta[i]
				temp_azim = sorted_azim[i]
				sorted_sta[i] = sorted_sta[j]
				sorted_azim[i] = sorted_azim[j]
				sorted_sta[j] = temp_sta
				sorted_azim[j] = temp_azim
	return sorted_sta, sorted_azim

# solves for the gap angle using azimuth from PLOT.OUT
def gap_angle(sta, azim):
	maximum = -math.inf
	stations = [str(), str()]
	start_end = [float(), float()]
	for i in range(len(azim) - 1):
		gap = azim[i+1] - azim[i]
		# print ("Gap angle between " + sta[i] + " and " + sta[i+1] + str(round(gap, 5)))
		if (gap > maximum):
			maximum = gap
			stations[0] = sta[i]
			stations[1] = sta[i+1]
			start_end[0] = 450 - azim[i+1]
			start_end[1] = 450 - azim[i]

	gap = azim[0] + 360 - azim[-1]
	# print ("Gap angle between " + sta[-1] + " and " + sta[0] + str(round(gap, 5)))
	if (gap > maximum):
		maximum = gap
		stations[0] = sta[0]
		stations[1] = sta[-1]
		start_end[0] = 450 - azim[0]
		start_end[1] = 450 - azim[-1]
	return maximum, stations, start_end


start = time.time()
STATMAIN = 'PHILSTA-main.DAT'
STATNAME, STATLAT, STATLON = get_station_locations(STATMAIN)

stat = 'PHILSTA.DAT'
statname, statlat, statlon = get_station_locations(stat)

stat1 = 'PLOT.DAT'
statname1, P, S = get_station_locations(stat1)

plot_out = 'PLOT.OUT'
ResP, ResS = get_residual(plot_out, statname1, S)

POINT_FILL_WITH_RECORD = 'red'
POINT_FILL_NO_RECORD = 'white'
STAR_FILL = 'yellow'

# A station in PHILSTA has a record if it is found in PHILSTA-main and PLOT.DAT
WITH_RECORD = [[], []] #long, lat
NO_RECORD = [[], []] #long, lat

for station in statname:
	if (station in STATNAME and station in statname1):
		index = STATNAME.index(station)
		WITH_RECORD[0].append(STATLON[index])
		WITH_RECORD[1].append(STATLAT[index])
	elif (station in STATNAME and station not in statname1):
		index = STATNAME.index(station)
		NO_RECORD[0].append(STATLON[index])
		NO_RECORD[1].append(STATLAT[index])


eplon, eplat = epicenter_location('PLOT.OUT')
STA, TOA, AZIM, DELTA, RESP, RESS, OBSP, OBSS, CALCP, CALCS = get_solution('PLOT.OUT')
TTMTAB, HEADER, NUMDEP, DEP1ST, DDELT, NUMDTA, DEP = read_table('JBTAB.PS')
DEPTH = get_depth('PLOT.OUT')


# interpolate to get time table for x = DEPTH OF EVENT (P time table)
DEPTH_P_TIMETABLE = []
for i in range(len(DEP)-1):
	d1 = float(DEP[i][0])
	d2 = float(DEP[i+1][0])
	if (DEPTH > d1 and DEPTH < d2):
		tab1 = [TTMTAB[j][i][0] for j in range(100)]
		tab2 = [TTMTAB[j][i+1][0] for j in range(100)]
		DEPTH_P_TIMETABLE = interpolate(d1, d2, tab1, tab2, DEPTH)
		break
	elif (DEPTH == d1):
		tab1 = [TTMTAB[j][i][0] for j in range(100)]
		DEPTH_P_TIMETABLE = tab1
		break

# interpolate to get time table for x = DEPTH OF EVENT (S time table)
DEPTH_S_TIMETABLE = []
for i in range(len(DEP)-1):
	d1 = float(DEP[i][1])
	d2 = float(DEP[i+1][1])
	if (DEPTH > d1 and DEPTH < d2):
		tab1 = [TTMTAB[j][i][1] for j in range(100)]
		tab2 = [TTMTAB[j][i+1][1] for j in range(100)]
		DEPTH_S_TIMETABLE = interpolate(d1, d2, tab1, tab2, DEPTH)
		break
	elif (DEPTH == d1):
		tab1 = [TTMTAB[j][i][1] for j in range(100)]
		DEPTH_S_TIMETABLE = tab1
		break

# the number of stations that are at most 200km away from the epicenter
W200 = within200(DELTA)


################## START OF FIRST PAGE ######################
fig = pygmt.Figure()

fig.shift_origin(yshift='1i')

# NO USE..
fig.coast(
    #region=[116, 130, math.floor(lowest_lat)-0.25, math.ceil(highest_lat)+0.25],	#[116, 130, 2, 22]
    region=[eplon-5, eplon+5, eplat-5, eplat+5],	#[116, 130, 2, 22]
    projection='M3i',
    shorelines=True,
    water='lightblue',
    land='237/201/175',
    frame=['WSne', 'af'],# '+tPhilippines'],
    resolution='f'
)
rad = 3 / (10) * (200 / 111) * 2
fig.plot(
	x=[eplon],
	y=[eplat],
	style="c" + str(rad) + "i",
	color="lightgreen", 
	pen="0.1p,black",
	transparency=50
)

rad = 3 / (10) * (100 / 111) * 2
sorted_sta, sorted_azim = sort_sta_azim(STA, AZIM)
gap, stations, angles = gap_angle(sorted_sta, sorted_azim)
gap = round(gap, 5)
station1 = [float(), float()]
station2 = [float(), float()]
for i in range(len(statname)):
	if (stations[0]+' ' == statname[i]):
		station1 = [statlon[i], statlat[i]]
	if (stations[1]+' ' == statname[i]):
		station2 = [statlon[i], statlat[i]]
data = np.array([[eplon, eplat, rad , angles[0], angles[1]]])
fig.plot(
	data=data, 
	style="w", 
	color="green", 
	pen="1p,black",
	transparency=50,
	# label="Gap_angle"
)
fig.plot(
    x=[station1[0], eplon, station2[0]],
    y=[station1[1], eplat, station2[1]],
    pen='1p,blue'
)

if (len(NO_RECORD[0]) != 0):
	fig.plot(
	    x=NO_RECORD[0],
	    y=NO_RECORD[1],
	    style='t0.1i',
	    color=POINT_FILL_NO_RECORD,
	    pen='black',
	    #label='No_Record',
	)
fig.plot(
    x=WITH_RECORD[0],
    y=WITH_RECORD[1],
    style='t0.1i',
    color=POINT_FILL_WITH_RECORD,
    pen='black',
    #label='With_Record',
    transparency=30
)
fig.plot(
    x=eplon,
    y=eplat,
    style='c0.1i',
    color=STAR_FILL,
    pen='black',
    #label='Epicenter',
)


fig.shift_origin(xshift='4i')

# GRAPH TRAVEL TIME TABLE
fig.basemap(
    region=[0, 15, 0, 400],
    projection='X3i',
    frame=['+t"Travel Time"']
)
x = [i for i in range(100)]
y_p = []
y_s = []


for i in range(NUMDEP[0]):
	if (DEPTH >= DEP[i][0]):
		continue
	else:
		i -= 1
		for j in range(15):
			y_p.append(TTMTAB[j][i][0])
		break

for i in range(NUMDEP[1]):
	if (DEPTH >= DEP[i][1]):
		continue
	else:
		i -= 1
		for j in range(15):
			y_s.append(TTMTAB[j][i][1])
		break

# GRAPH OF P TIME TABLE
fig.plot(
    x=x,
    y=DEPTH_P_TIMETABLE,
    pen='1p,red',
#     frame=['a', 'WSne'],
    frame=["WSne", 'xaf+l"Delta (degrees)"', 'yaf+l"Time (seconds)"'],
    label='P',
)
X_stat = [float(delta) for delta in DELTA]
Yp = [float(calcp) for calcp in CALCP]
fig.plot(
    x=X_stat,
    y=Yp,
    style='x0.05i',
    color='red',
    pen='1p,red',
    transparency=30
)
print (x[0], y_p[0])
print (x[-1], y_p[-1])
print (X_stat[0], X_stat[-1])
print (Yp[0], Yp[-1])

# GRAPH OF S TIME TABLE
fig.plot(
    x=x,
    y=DEPTH_S_TIMETABLE,
    pen='1p,blue',
    frame=['af', 'WSne'],
    label='S',
)
X_stat = [float(delta) for delta in DELTA]
Ys = [float(calcs) for calcs in CALCS]
fig.plot(
    x=X_stat,
    y=Ys,
    style='x0.05i',
    color='blue',
    pen='1p,blue',
    transparency=30
)
print (x[0], y_s[0])
print (x[-1], y_s[-1])
print (X_stat[0], X_stat[-1])
print (Ys[0], Ys[-1])

fig.legend(position="jTL+o0.1c", box=False)



fig.shift_origin(xshift='-2.5i', yshift='4i')

# PLOT THE STATIONS IN PHILSTA

# rad = 4 / (130 - 116) * (200 / 111) * 2
# sorted_sta, sorted_azim = sort_sta_azim(STA, AZIM)
# gap, stations, angles = gap_angle(sorted_sta, sorted_azim)
# gap = round(gap, 5)
# station1 = [float(), float()]
# station2 = [float(), float()]
# for i in range(len(statname)):
# 	if (stations[0]+' ' == statname[i]):
# 		station1 = [statlon[i], statlat[i]]
# 	if (stations[1]+' ' == statname[i]):
# 		station2 = [statlon[i], statlat[i]]
# print (station1)
# print (station2)
# print (angles)

fig.coast(
    #region=[116, 130, math.floor(lowest_lat)-0.25, math.ceil(highest_lat)+0.25],	#[116, 130, 2, 22]
    region=[116, 130, 2, 22],	#[116, 130, 2, 22]
    projection='M4i',
    shorelines=True,
    water='lightblue',
    land='237/201/175',
    frame=['af'],# '+tPhilippines'],
    resolution='f'
)

# GRAPH OF WEDGE (GAP ANGLE)
# rad = 4 / (130 - 116) * (100 / 111) * 2
# data = np.array([[eplon, eplat, rad , angles[0], angles[1]]])
# fig.plot(
# 	data=data, 
# 	style="w", 
# 	color="green", 
# 	pen="1p,black",
# 	transparency=50,
# 	# label="Gap_angle"
# )

# CONNECT 2 STATIONS AND EPICENTER WHICH FORMS THE GAP ANGLE
# fig.plot(
#     x=[station1[0], eplon, station2[0]],
#     y=[station1[1], eplat, station2[1]],
#     pen='1p,blue'
# )

# STATIONS WITH RECORD BUT ARE NOT USED IN COMPUTATION
if (len(NO_RECORD[0]) != 0):
	fig.plot(
	    x=NO_RECORD[0],
	    y=NO_RECORD[1],
	    style='i0.1i',
	    color=POINT_FILL_NO_RECORD,
	    pen='black',
	    label='WRecNotUsed',
	)

# STATIONS WITH RECORD THAT ARE USED IN COMPUTATION
fig.plot(
    x=WITH_RECORD[0],
    y=WITH_RECORD[1],
    style='i0.1i',
    color=POINT_FILL_WITH_RECORD,
    pen='black',
    label='WRecUsed',
    transparency=30
)

# PLOT THE EPICENTER
fig.plot(
    x=eplon,
    y=eplat,
    style='c0.1i',
    color=STAR_FILL,
    pen='black',
    label='Epicenter',
)

fig.legend()

fig.savefig('Philippines.pdf')
################### END OF FIRST PAGE #######################

###2nd page
fig = pygmt.Figure()

pygmt.makecpt(cmap='polar',series=[-1,1])

fig.basemap(region=[0, 20, 0, 20], projection="X9i", frame="WSen", transparency=100)
xcoor = [0, 1, 2.5, 4, 5.5, 7, 8.5, 10, 11.5, 13]
labels = ['STA', 'TOA', 'AZIM', 'DELTA', 'RESp', 'RESs', 'OBSp', 'OBSs', 'CALCp', 'CALCs']
for i in range(10):
    fig.text(text=labels[i], x=xcoor[i], y=19, font="10p,Helvetica", justify='ML')
#fig.text(text="STA  TOA  AZIM  DELTA RESp  RESs  OBSp  OBSs  CALCp CALCs", x=1, y=19, font="10p,Helvetica", justify='ML')
ycoor = 19
obss_calcs_zero = [[], []]
# print (STA)
for i in range(len(STA)):
	if (float(CALCS[i]) == 0 and float(OBSS[i]) == 0):
		obss_calcs_zero[0].append(STATLON[STATNAME.index(STA[i]+' ')])
		obss_calcs_zero[1].append(STATLAT[STATNAME.index(STA[i]+' ')])
for i in range(len(STA)):
	ycoor -= 0.3
	if (float(OBSS[i])==0 and (float(CALCS[i]) == 0)):
		OBSS[i] = '   --------'
		CALCS[i] = '   --------'
	fig.text(text=STA[i], x=xcoor[0], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=format(float(TOA[i]), '.4f').zfill(8), x=xcoor[1], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=format(float(AZIM[i]), '.4f').zfill(8), x=xcoor[2], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=DELTA[i], x=xcoor[3], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=RESP[i], x=xcoor[4], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=RESS[i], x=xcoor[5], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=OBSP[i], x=xcoor[6], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=OBSS[i], x=xcoor[7], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=CALCP[i], x=xcoor[8], y=ycoor, font="10p,Helvetica", justify='ML')
	fig.text(text=CALCS[i], x=xcoor[9], y=ycoor, font="10p,Helvetica", justify='ML')
	


P_arr, S_arr = ps_arrival(ResP, ResS)


# for i in range(len(AZIM)):
# 	print (sorted_sta[i] + "\t" + str(sorted_azim[i]))

print ("Gap Angle: " + str(gap) + " between " + stations[0] + " and " + stations[1])


fig.text(text="Number of Stations with Record:  " + str(len(statname)), x=14.5, y=19, font="10p,Helvetica", justify='ML')
fig.text(text="Number of Stations with P-arrivals:  " + str(P_arr), x=14.5, y=18.5, font="10p,Helvetica", justify='ML')
fig.text(text="Number of Stations with S-arrivals:  " + str(S_arr), x=14.5, y=18, font="10p,Helvetica", justify='ML')
fig.text(text="Number of Stations within:  " + str(W200), x=14.5, y=17.5, font="10p,Helvetica", justify='ML')
fig.text(text="200km radius", x=15, y=17.0, font="10p,Helvetica", justify='ML')
fig.text(text="Gap Angle: " + str(gap) + " between ", x=14.5, y=16.5, font="10p,Helvetica", justify='ML')
fig.text(text=stations[0] + " and " + stations[1], x=16.5, y=16, font="10p,Helvetica", justify='ML')


fig.shift_origin(yshift='3.5i')
fig.shift_origin(xshift='5i')


fig.shift_origin(yshift='6.5i') #7i
fig.coast(
    #region=[116, 130, math.floor(lowest_lat)-0.25, math.ceil(highest_lat)+0.25],   #[116, 130, 2, 22]
    region=[116, 130, 2, 22],   #[116, 130, 2, 22]
    projection='M4i',
    shorelines=True,
    water='lightblue',
    land='237/201/175',
    frame=['af'],# '+tPhilippines'],
    resolution='f'
)
rad = 4 / (130 - 116) * (200 / 111) * 2
# fig.plot(
# 	x=[eplon],
# 	y=[eplat],
# 	style="c" + str(rad) + "i",
# 	color="lightgreen", 
# 	pen="0.1p,black",
# 	transparency=50
# )

if (len(NO_RECORD[0]) != 0):
	fig.plot(
	    x=NO_RECORD[0]+obss_calcs_zero[0],
	    y=NO_RECORD[1]+obss_calcs_zero[1],
	    style='i0.1i',
	    color='gray',#POINT_FILL_WITH_RECORD,
	    pen='black',
	    label='Unused_S/NoRecS',
	    #transparency=30
	)
WITH_S_RECORD = [[],[]]
for i in range(len(statname1)):
	if (STA[i] + ' ' in statname1 and S[i] != '       '):
		WITH_S_RECORD[0].append(statlon[statname.index(STA[i]+' ')])
		WITH_S_RECORD[1].append(statlat[statname.index(STA[i]+' ')])
# print (len(WITH_S_RECORD[0]))
# print (len(WITH_S_RECORD[1]))
# print (len(ResS))
fig.plot(
    x=WITH_S_RECORD[0],
    y=WITH_S_RECORD[1],
    style='i0.1i',
    color=ResS,#POINT_FILL_WITH_RECORD,
    pen='black',
    cmap=True,
    # label='Used_S',
    #transparency=30
)
fig.colorbar(frame='af+l"ResS"')
fig.plot(
    x=eplon,
    y=eplat,
    style='c0.1i',
    color=STAR_FILL,
    pen='black',
    label='Epicenter',
    #transparency=30
)
fig.legend()

fig.shift_origin(xshift='-5i')
fig.coast(
    #region=[116, 130, math.floor(lowest_lat)-0.25, math.ceil(highest_lat)+0.25],   #[116, 130, 2, 22]
    region=[116, 130, 2, 22],   #[116, 130, 2, 22]
    projection='M4i',
    shorelines=True,
    water='lightblue',
    land='237/201/175',
    frame=['af'],# '+tPhilippines'],
    resolution='f'
)
rad = 4 / (130 - 116) * (200 / 111) * 2
# fig.plot(
# 	x=[eplon],
# 	y=[eplat],
# 	style="c" + str(rad) + "i",
# 	color="lightgreen", 
# 	pen="0.1p,black",
# 	transparency=50
# )
if (len(NO_RECORD[0]) != 0):
	fig.plot(
	    x=NO_RECORD[0],
	    y=NO_RECORD[1],
	    style='i0.1i',
	    color='black',#POINT_FILL_WITH_RECORD,
	    pen='black',
	    label='Unused_P',
	    #transparency=30
	)

fig.plot(
    x=WITH_RECORD[0],
    y=WITH_RECORD[1],
    style='i0.1i',
    color=ResP,#POINT_FILL_WITH_RECORD,
    pen='black',
    cmap=True,
    # label='Used_P',
    #transparency=30
)
fig.colorbar(frame='af+l"ResP"')
fig.plot(
    x=eplon,
    y=eplat,
    style='c0.1i',
    color=STAR_FILL,
    pen='black',
    label='Epicenter',
    #transparency=30
)

fig.legend()
## 2nd page end
fig.savefig("RES.pdf")

####################################


####################################

end = time.time()

f = open('time.txt', 'w')
f.write('Runnning time: ' + str(end - start) + '\n')
f.close()

#----------------------------------------------------------------------------------------------------------------#

# oahu = [-158.3, -157.6, 21.2, 21.8]
# fig = pygmt.Figure()
# for res in ["c", "l", "i", "h", "f"]:
#     fig.coast(resolution=res, shorelines="1p", region=oahu, projection="M5c")
#     fig.shift_origin(xshift="5c")
# fig.show(method='external')

# grid = pygmt.datasets.load_earth_relief(
# 	resolution="30s", 
# 	region=[116, 130, 2, 22]
# )

# fig = pygmt.Figure()
# fig.grdimage(
# 	grid=grid, 
# 	projection="M12i", 
# 	frame="afg", 
# 	cmap="relief"
# )
# fig.colorbar(
# 	frame=["a1000", "x+lElevation", "y+lm"]
# )
