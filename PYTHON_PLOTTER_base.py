import math, re
#from vincenty import vincenty

def get_number_of_stations(filename):
	f = open(filename)
	lines = f.readlines()
	f.close()
	return len(lines)

def read_table(jbtab):
	#open time table
	f = open(jbtab)

	#store all lines in file (for processing)
	lines = []

	for line in f:
	    line = line.strip('\n')                  #removing new line
	    line = re.sub(' +', ' ', line.lstrip())  #removing multiple spaces
	    lines.append(line)
	f.close()
	#line counter
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

def print_table(header, numdep, dep1st, ddelt, numdta, dep, ttmtab):
    for i in range(len(header)):
        print ("HEADER: " + str(header[i]))
        print ("NUMDEP: " + str(numdep[i]))
        print ("DEP1ST: " + str(dep1st[i]))
        print ("DDELT: " + str(DDELT[i]))
        print ("NUMDTA: " + str(numdta[i]))

        for j in range(numdep[i]):
            print (dep[j][i])
            string = ""
            index = 0
            for k in range(numdta[i]):
            	string += str(ttmtab[k][j][i])
            	index += 1
            	if (index % 9 == 0):
            		print (string+'\n')
            		string = ""
            		index = 0
            	else:
            		string += '\t'
            if (index % 9 != 8):
            	print (string)

def read_stations(STAT, WWSS, ADLAT, ADLON, SELEV, SCORR):
	lines = []

	f = open(STAT)
	for line in f:
	    line = line.strip('\n')
	    lines.append(line)
	f.close()

	for i in range(NUMSTA):
		line = lines[i]
		WWSS[i] = line[0:4]
		ADLAT[i] = float(line[4:14])
		ADLON[i] = float(line[14:24])
		SELEV[i] = float(line[24:30]) / 1000
		try:
			SCORR[i] = float(line[30:36])
		except:
			SCORR[i] = 0.0

	return WWSS, ADLAT, ADLON, SELEV, SCORR

def read_plot(PLOT, SS, ISTA, WWSS, TOBS, WT, NUMSTA, OUTPUT):
	lines = []

	f = open(PLOT)
	for line in f:
	    line = line.strip('\n')
	    if (line == 'XXX'):
	        break
	    else:
	        lines.append(line)
	f.close()

	line = lines[0]
	IY = line[0:2]
	MON = line[2:4]
	IDAY = line[4:6]
	IH =line[6:8]
	MINT = line[8:10]
	SECD = float(line[11:15].lstrip())
	OLAT = float(line[15:22].lstrip())
	OLON = float(line[22:29].lstrip())
	DEPP = float(line[29:34].lstrip())
	NSTA = 0
	HREF = float(IH) * 3600
	OT = HREF + float(MINT) * 60 + SECD
	date = str(int(IY + MON + IDAY)).rjust(6)
	OUTPUT.write(date + '\n')
	lines = lines[1:]
	for i in range(len(lines)):
	    line = lines[i]
	    AS = line[0:4]
	    IWP = line[4:6].lstrip().zfill(2)
	    IMINP = line[6:9].lstrip().zfill(3)
	    TSECP = line[9:14].lstrip().zfill(5)
	    IWS = line[14:16].lstrip().zfill(2)
	    IMINS = line[16:19].lstrip().zfill(2)
	    TSECS = line[19:24].lstrip().zfill(5)
	    # print (AS + '\t' + IWP + '\t' + IMINP + '\t' + TSECP + '\t' + IWS + '\t' + IMINS + '\t' + TSECS)
	    if (AS == "XXX"):
	        break
	    SS[i] = AS
	    index_AS = binary_search(WWSS, 0, NUMSTA-1, AS)
	    # if (index_AS != -1):
	    # 	NSTA += 1
	    NSTA += 1
	    ISTA[i] = index_AS
	    WP = 1.0 - float(IWP) / 4.0
	    WS = 1.0 - float(IWS) / 4.0
	    WT[i][0] = WP
	    WT[i][1] = WS
	    TP = float(IMINP) * 60 + float(TSECP)
	    if (TP == 0):
	    	TOBS[i][0] = round(TP, 5)
	    else:
	    	TOBS[i][0] = round(TP + HREF, 5)
	    TS = float(IMINS) * 60 + float(TSECS)
	    if (TS == 0):
	    	TOBS[i][1] = round(TS, 5)
	    else:
	    	TOBS[i][1] = round(TS + HREF, 5)

	    date = '20'+IDAY + '_' + IY + MON + '_' + IH + MINT
	return SS, ISTA, TOBS, WT, NSTA, OT, OLAT, OLON, DEPP, date

def binary_search(array, low, high, key):
	if (high >= low):
		mid = int((low + high) / 2)
		if (array[mid] == key):
			return mid
		elif (array[mid] > key):
			return binary_search(array, low, mid-1, key)
		else:
			return binary_search(array, mid+1, high, key)
	else:
		return -1

def fnasin(x):
	if (abs(x) < 1):
		return math.atan(x / math.sqrt(1 - x**2))
	else:
		return 1.570796

def buildb(NPAR, NOBS, D, RES, Z, B, THETA):
	for k in range(NPAR):
		Z[k] = float()
		for l in range(k+1):
			B[k][l] = float()
			for i in range(NOBS):
				B[k][l] = B[k][l] + D[i][l]*D[i][k]
		for i in range(NOBS):
			Z[k] = Z[k] + RES[i]*D[i][k]
	for i in range(NPAR):
		B[i][i] = B[i][i] + THETA**2

	return

def gjinv(NCOL, B, Z, INDEX):
	ISING = 0
	I3, I4 = float(), float()
	for k in range(NCOL):
		for l in range(k+1):
			bb = B[k][l]
			B[l][k] = bb

	for i in range(NCOL):
		INDEX[i][2] = 0

	for i in range(NCOL):
		B1 = 0
		for J in range(NCOL):
			if (INDEX[J][2] == 1):
				continue
			else:
				for IT in range(NCOL):
					if (INDEX[IT][2] > 1):
						ISING = -1
						return
					if (INDEX[IT][2] == 1):
						continue
					if (B1 == abs(B[J][IT])):
						continue
					I3 = J
					I4 = IT
					B1 = abs(B[J][IT])
		I43 = INDEX[I4][2]
		INDEX[I4][2] = I43 + 1
		INDEX[i][0] = I3
		INDEX[i][1] = I4
		
		if (I3 != I4):
			for L in range(NCOL):
				T1 = B[I3][L]
				T2 = B[I4][L]
				B[I3][L] = T2
				B[I4][L] = T1
			T1 = z[I3]
			T2 = Z[I4]
			Z[I3] = T2
			Z[I4] = T1

		PIVOT = B[I4][I4]
		B[I4][I4] = 1
		for L in range(NCOL):
			BI4L = B[I4][L]
			B[I4][L] = BI4L / PIVOT
		ZI4 = Z[I4]
		Z[I4] = ZI4 / PIVOT

		for L1 in range(NCOL):
			if (L1 == I4):
				continue
			T = B[L1][I4]
			B[L1][I4] = 0.0
			for L in range(NCOL):
				BI4L = B[I4][L]
				BL1L = B[L1][L]
				B[L1][L] = BL1L - BI4L * T
			ZI4 = Z[I4]
			ZL1 = Z[L1]
			Z[L1] = ZL1 - ZI4 * T

	for I in range(NCOL):
		L = NCOL - I - 1
		if (INDEX[L][0] == INDEX[L][1]):
			continue
		I3 = INDEX[L][0]
		I4 = INDEX[L][1]
		for IT in range(NCOL):
			T1 = B[IT][I3]
			T2 = B[IT][I4]
			B[IT][I3] = T2
			B[IT][I4] = T1
	for IT in range(NCOL):
		if (INDEX[IT][2] != 1):
			ISING = -1
			break
	
	return ISING

def DELAZ(slat, slon, eplat, eplon):
	# if (slat == 14.3500004 and ITER == 0):
	# 	print (slat, slon, eplat, eplon)
	F = 0.01745329
	tslat = slat * F
	tslon = slon * F
	# if (slat == 14.3500004 and ITER == 0):
	# 	print (tslat, tslon)
    
	glat = math.atan(0.993277 * math.tan(tslat))
	dca = math.cos(glat) * math.cos(tslon)
	dcb = math.cos(glat) * math.sin(tslon)
	dcc = math.sin(glat)
	slat = tslat / F

	geplat = math.atan(0.993277* math.tan(eplat*F))
	epdca = math.cos(geplat) * math.cos(eplon*F)
	epdcb = math.cos(geplat) * math.sin(eplon*F)
	epdcc = math.sin(geplat)

	par1 = 1 - 0.5 * ((dca - epdca)**2 + (dcb - epdcb)**2 + (dcc - epdcc)**2)
	delta = 57.29578 * math.atan(math.sqrt((1.0/par1**2) - 1))
	if (par1 < 0):
	    delta = 180 - delta
	if (delta == 0):
	    delta = 0.001
	t1 = dca - math.sin(eplon*F)
	t2 = dcb + math.cos(eplon*F)
	t3 = math.sin(delta*F)
	par2 = (0.5 * (t1**2 + t2**2 + dcc**2) - 1) / t3
	t1 = dca - math.sin(geplat) * math.cos(eplon*F)
	t2 = dcb - math.sin(geplat) * math.sin(eplon*F)
	t4 = dcc + math.cos(geplat)
	apar2 = abs(par2)

	if (apar2 < 1):
	    if (par2 == 0):
	        par2 = 0.001
	    if (par2 == 1):
	        par2 = 0.999
	    azim = 57.29578 * math.atan(1.0 / math.sqrt((1.0/par2**2) - 1))
	else:
	    azim = 90

	par3 = (0.5 * (t1**2 + t2**2 + t4**2) - 1) / t3

	if (par2 >= 0):
	    if (par3 < 0):
	        azim = 180 - azim
	        return [delta,azim]
	    else:
	        return [delta, azim]

	if (par3 < 0):
	    azim = azim + 180
	    return [delta,azim]

	else:
	    azim = 360 - azim
	    return [delta, azim]


############################################################################            	
NSTMAX = 150
NWSMAX = 200
NPH = 2

TTMTAB = [[[None for k in range(2)] for j in range(15)] for i in range(120)]	
DEP = [[None for j in range(2)] for i in range(15)]								
PVSURF = [None for i in range(2)]												
DEP1ST = [None for i in range(2)]												
DDELT = [None for i in range(2)]												
NUMDTA = [None for i in range(2)]												
NUMDEP = [None for i in range(2)]												
D = [[float() for j in range(4)] for i in range(90)]
TRES = [[None for j in range(2)] for i in range(90)]
RES = [float() for i in range(300)]
B = [[float() for j in range(4)] for i in range(4)]
BDIAG = [float() for i in range(4)]
Z = [float() for i in range(4)]
INDEX = [[None for i in range(3)] for i in range(4)]
SS = [str() for i in range(NSTMAX)]
TOBS = [[None for j in range(2)] for i in range(90)]
WT = [[float() for j in range(2)] for i in range(90)]
WTFAC = [[None for j in range(2)] for i in range(90)]
PTOA = [None for i in range(90)]
KFM = [[None for j in range(2)] for i in range(90)]		#NOT USED
DELTA = [None for i in range(90)]
TCALC = [[None for j in range(2)] for i in range(90)]
AZIM = [None for i in range(90)]
ISTA = [None for i in range(90)]
FMS = [None for i in range(6)]							#NOT USED
WWSS = [str() for i in range(NWSMAX)]
ADLAT = [None for i in range(NWSMAX)]
ADLON = [None for i in range(NWSMAX)]
SELEV = [None for i in range(NWSMAX)]
SCORR = [None for i in range(NWSMAX)]
HEADER = [None for i in range(2)]
TTAB = [None for i in range(120)]
TC1 = [None for i in range(90)]
TC2 = [None for i in range(90)]

AS = str()
YS = str()
OUT = str()
TTMTBL = str()
STAT = str()
INPUT = str()
RPD = float()
WP = float()
WTA = float()
RMS = float()
WS = float()
RESCUT = float()

PII = math.pi
DPR = 180 / PII
RPD = 1 / DPR
ITRUE = 1
IFALSE = 0

###############################################################################
R = 20
if (R > 0):
	RESCUT = R
else:
	RESCUT = 60

THETA = 0.1
ADJHYP = 1
ITERAN = 50
YS = 'N'
NPARS = 4
NUMSTA = 0
STAT = 'C:/EQP11-20/Programs/PHILSTA.DAT'
NUMSTA = get_number_of_stations(STAT)
PVSURF[0] = 5
PVSURF[1] = PVSURF[0] / 1.75

TTMTBL = "C:/EQP11-20/Programs/JBTAB.PS"
TTMTAB, HEADER, NUMDEP, DEP1ST, DDELT, NUMDTA, DEP = read_table(TTMTBL)
# print_table(HEADER, NUMDEP, DEP1ST, DDELT, NUMDTA, DEP, TTMTAB)

WWSS, ADLAT, ADLON, SELEV, SCORR = read_stations(STAT, WWSS, ADLAT, ADLON, SELEV, SCORR)

INPUT = "C:/EQP11-20/Programs/PLOT.DAT"
OUTPUT = open("C:/EQP11-20/Programs/PLOT.OUT", 'w')
SS, ISTA, TOBS, WT, NSTA, OT, OLAT, OLON, DEPP, date = read_plot(INPUT, SS, ISTA, WWSS, TOBS, WT, NUMSTA, OUTPUT)

NPAR = int()
NOBS = int()
ITSTOP = IFALSE
ITLAST = int()
RCUT = float()

OUTPUT.write("IT    LAT     LON      DEPTH HR MIN SEC    RMS\n")


for ITER in range(ITERAN):
	if (ITER+1 == ITERAN or ITSTOP != 0):
		ITLAST = ITRUE
	else:
		ITLAST = IFALSE
	SUMWT = 0.0
	RMS = 0.0

	IAH = int(OT / 3600)
	AH = float(IAH)
	TTIME = OT - AH * 3600
	IAM = int(TTIME/60)
	AM = float(IAM)
	ASEC = round(TTIME - AM*60, 10)
	# print (IAH, IAM, ASEC)
	
	if (ITER == 0):
		NPAR = 3 
	else:
		NPAR = NPARS
	Z[3] = 0
	NOBS = -1

	# print (ITER)
	for KSTA in range(NSTA):
		IST = ISTA[KSTA]
		if (IST == -1):
			continue
		# if (ITER == 0 and KSTA == 0):
		# 	if (ADLAT[IST] == 14.35):
		# 		ADLAT[IST] = 14.3500004
		# 		ADLON[IST] = 121.213997
		# 		OLAT = 14.5100002
		# 		OLON = 121.199997
				# print (ADLAT[IST], ADLON[IST], OLAT, OLON)
		DELTB, DAZ = DELAZ(ADLAT[IST], ADLON[IST], OLAT, OLON)
		DELTA[KSTA] = DELTB
		AZIM[KSTA] = DAZ
		PTOA[KSTA] = 0
		# if (ITER == 0 and KSTA == 0):
		# 	print (DELTB, DAZ)

		for IPH in range(NPH):
			IDEL = int((DELTB-DEP1ST[IPH]) / DDELT[IPH]) + 1
			if (IDEL >= NUMDTA[IPH] or IDEL < 1):
				TTIME = 0
				continue
			INDT = int(DELTB / DDELT[IPH])
			DDEL = DELTB / DDELT[IPH] - float(INDT)
			IDEP = NUMDEP[IPH] - 1
			for I in range(NUMDEP[IPH]-1):
				if (DEPP >= DEP[I][IPH] and DEPP < DEP[I+1][IPH]):
					IDEP = I
			DDEP = (DEPP - DEP[IDEP][IPH]) / (DEP[IDEP+1][IPH] - DEP[IDEP][IPH])
			T0 = TTMTAB[IDEL-1][IDEP][IPH]
			T2 = TTMTAB[IDEL][IDEP][IPH] - T0
			T3 = TTMTAB[IDEL-1][IDEP+1][IPH] - T0
			T4 = TTMTAB[IDEL][IDEP+1][IPH] - T0
			TTIME = T0 + T2*DDEL + T3*DDEP + (T4-T3-T2)*DDEL*DDEP
			DTDH = T2 / DDELT[IPH] / 111.19
			DTDZ = T3 / (DEP[IDEP+1][IPH] - DEP[IDEP][IPH])

			VELP = 1 / math.sqrt(DTDH**2 + DTDZ**2)
			if (IPH == 0):
				PTOA[KSTA] = fnasin(VELP*DTDH) * DPR
				if (DTDZ > 0):
					PTOA[KSTA] = 180 - PTOA[KSTA]

			if (TOBS[KSTA][IPH] == 0):
				WTFAC[KSTA][IPH] = 0
				TCALC[KSTA][IPH] = 0
				TRES[KSTA][IPH] = 0
				continue

			TTIME = TTIME + SCORR[IST] + SELEV[IST] * math.sqrt(1 / (PVSURF[IPH]**2) - DTDH**2)
			TCALC[KSTA][IPH] = TTIME

			TRES[KSTA][IPH] = TOBS[KSTA][IPH] - TTIME - OT 
			TRESA = TRES[KSTA][IPH]
			ABRES = abs(TRESA)

			WTFAC[KSTA][IPH] = 1
			if (ITER > 1):
				RCUT = RESCUT
			else:
				RCUT = 5

			if (ABRES > RCUT):
				WTFAC[KSTA][IPH] = 0.5 * (1 + math.cos(PII * (ABRES-RCUT) / RCUT))
			if (ABRES > 2*RCUT):
				WTFAC[KSTA][IPH] = 0
			WTA = WT[KSTA][IPH] * WTFAC[KSTA][IPH]
			if (WTA == 0):
				continue
			
			SUMWT = SUMWT + WTA 
			RMS = RMS + TRESA**2 * WTA**2
			if (ITLAST != 0):
				continue

			NOBS = NOBS + 1
			RES[NOBS] = TRES[KSTA][IPH] * WTA

			# print (NOBS)
			D[NOBS][0] = 1.0 * WTA
			D[NOBS][1] = -math.cos(DAZ*RPD) * DTDH * WTA
			D[NOBS][2] = -math.sin(DAZ*RPD) * DTDH * WTA
			D[NOBS][3] = DTDZ * WTA

	if (SUMWT == 0):
		OUTPUT.write ('SUM OF WEIGHT = 0')
	else:
		DOF = SUMWT - NPAR
		if (DOF <= 0):
			DOF = 1
		RMS = math.sqrt(RMS / DOF)
		if (ITLAST != 0):
			# print (ITER, OLAT, OLON, DEPP, IAH, IAM, ASEC, RMS)
			iterr = str(ITER+1).rjust(3)
			olat = format(OLAT, '.3f').rjust(9)
			olon = format(OLON, '.3f').rjust(9)
			depp = format(DEPP, '.2f').rjust(7)
			iah = str(IAH).rjust(3)
			iam = str(IAM).rjust(3)
			asec = format(ASEC, '.2f').rjust(6)
			rms = format(RMS, '.2f').rjust(7)
			OUTPUT.write(iterr + olat + olon + depp + iah + iam + asec + rms + '\n')	

			OUTPUT.write("\nERR   DEG     DEG      KM           SEC \n")
			ABADA = math.sqrt(BDIAG[1]) * RMS / 111.2
			ABADE = math.sqrt(BDIAG[2]) * RMS / 111.2
			ABADI = math.sqrt(BDIAG[3]) * RMS
			ABADO = math.sqrt(BDIAG[0]) * RMS
			abada = format(ABADA, '.4f').rjust(6)
			abade = format(ABADE, '.4f').rjust(6)
			abadi = format(ABADI, '.2f').rjust(5)
			abado = format(ABADO, '.2f').rjust(8)
			OUTPUT.write(6*" " + abada + 3*" " + abade + 2*" " + abadi + 4*" " + abado + '\n')
			
			# print (ABADA, ABADE, ABADI, ABADO)
			break

		if (ITER == 0):
			for IKL in range(4):
				B[IKL][3] = 0
				B[3][IKL] = 0

		buildb(NPAR, NOBS+1, D, RES, Z, B, THETA)
	
		ISING = gjinv(NPAR, B, Z, INDEX)

		for I in range(NPAR):
			BDIAG[I] = B[I][I]
		if (ISING != 0):
			ITSTOP = ITRUE
			continue

		ADJ = math.sqrt(Z[1]**2 + Z[2]**2 + Z[3]**2)
		if (ITER > 1):
			if (ADJ < ADJHYP):
				ITSTOP = ITRUE
		OT = OT + Z[0]
		OLON = OLON + Z[2] / 111.19
		OLAT = OLAT + Z[1] / 111.19
		if (NPAR == 4):
			DEPP = DEPP + Z[3]
		if (DEPP < 0):
			DEPP = 1

	# print (ITER, OLAT, OLON, DEPP, IAH, IAM, ASEC, RMS)

# print ('\n\n')

OUTPUT.write ("\nSTA   TOA      AZIM     DELTA    RESp     RESs     OBSp     OBSs     CALCp    CALCs\n")
for I in range(NSTA):
	if (ISTA[I] == -1):
		OUTPUT.write ("STATION NOT IN LIST\n")
	else:
		if (TOBS[I][0] == 0.0):
			TC1[I] = 0.0
		else:
			TC1[I] = TOBS[I][0] - OT
		if (TOBS[I][1] == 0.0):
			TC2[I] = 0.0
		else:
			TC2[I] = TOBS[I][1] - OT
		WT[I][0] = WT[I][0] * WTFAC[I][0]
		WT[I][1] = WT[I][1] * WTFAC[I][1]
		ss = SS[I][0:3]
		ptoa = str(format(round(PTOA[I], 4),'.4f')).rjust(9)
		azim = str(format(round(AZIM[I], 4),'.4f')).rjust(9)
		delta = str(format(round(DELTA[I], 4),'.4f')).rjust(9)
		tres0 = str(format(round(TRES[I][0], 4),'.4f')).rjust(9)
		tres1 = str(format(round(TRES[I][1], 4),'.4f')).rjust(9)
		tc1 = str(format(round(TC1[I], 4),'.4f')).rjust(9)
		tc2 = str(format(round(TC2[I], 4),'.4f')).rjust(9)
		tcalc1 = str(format(round(TCALC[I][0], 4),'.4f')).rjust(9)
		tcalc2 = str(format(round(TCALC[I][1], 4),'.4f')).rjust(9)
		OUTPUT.write (ss + ptoa + azim + delta + tres0 + tres1 + tc1 + tc2 + tcalc1 + tcalc2 + '\n')
		

OUTPUT.close()
