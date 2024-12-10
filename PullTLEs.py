import spacetrack.operators as op
from spacetrack import SpaceTrackClient
import datetime as dt
from time import sleep
import csv
from pathlib import Path

# Original code from Thomas G. Roberts at the MIT ARCLab
# https://github.com/ARCLab-MIT/GEO-Toolbox/blob/main/downloadTLEs.py

# Check whether ./Data/TLEs/ exists. If not, make it.
path = './Data/TLEs/'
Path(path).mkdir(parents=True, exist_ok=True)

st_email = "EMAIL"
st_pass = "PASSWORD"

# Log in to Space-Track using your email and password
st = SpaceTrackClient(identity=st_email, password=st_pass)

# Make a list of all the satcats in Data/satcats.csv
satcats = []
with open("./Data/satcats2.csv", encoding='utf-8-sig') as f:
	reader = csv.reader(f, delimiter=",")
	for row in reader:
		for sat in row:
			satcats.append(sat)

studyperiod_start = "1957-10-04"
studyperiod_end = "2024-12-04"

# Only pull TLEs from between the start date and the end date
drange = op.inclusive_range(dt.datetime(int(studyperiod_start[0:4]), int(studyperiod_start[5:7]), int(studyperiod_start[8:10])), dt.datetime(int(studyperiod_end[0:4]), int(studyperiod_end[5:7]), int(studyperiod_end[8:10])))

# Download the TLEs and save them in Data/TLEs/[satcat].txt
for satcat in satcats:
	while True:
		try:
			with open('./Data/TLEs/' + str(satcat) + '.txt', 'w') as f:
				f.write(st.gp_history(norad_cat_id=satcat, epoch=drange, orderby='epoch desc', format='tle'))
				f.close()
			print("Printed file: " + str(satcat) + ".txt.")
			sleep(15)
			break
		except:
			print("Failed to get item: " + str(satcat) + ".txt - trying again")
			sleep(15)
			continue

