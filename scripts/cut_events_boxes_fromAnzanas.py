####
# Make event files for all events in catalog, for all stations available
# VJS 6/2017
####

import waveforms as wf
import numpy as np
from obspy.core import UTCDateTime

# Path to the event box catalog file:
catalogfile = '/Users/vsahakian/iris/play_data/catalog/Imperial_Valley.txt'

# Main anzanas directory:
anzanas_dir = '/net/anzanas/data/ANZA_waveforms/'

#############################################################################
# Read in catalog file - in floats, and strings:
evcatalog_floats = np.genfromtxt(catalogfile,usecols=(0,1,2,3))
evcatalog_strings = np.genfromtxt(catalogfile,usecols=(4,5),dtype='S')

# Collect columns of data from floats::
evlon = evcatalog_floats[:,0]
evlat = evcatalog_floats[:,1]
evdepth = evcatalog_floats[:,2]
evmag = evcatalog_floats[:,3]

# Collect columns of string data, origin time and evend id's:
evorigin = evcatalog_strings[:,0]
evid = evcatalog_strings[:,1]

##########################
# Loop over the events
#   For every event, get the event info, and then find all files from that 
#   day and cut them.

for eventi in range(len(evid)):
    evlon_i = evlon[eventi]
    evlat_i = evlat[eventi]
    evdepth_i = evdepth[eventi]
    evmag_i = evmag[eventi]
    
    # Event origin time needs to be converted to a utcdatetime object:
    evorigin = UTCDateTime(evorigin[eventi])
    # Remove the ci from the event id
    evid = evid[eventi].split('ci')[1]
    
    # Now get the year and julian day:
    evyear_i = evorigin.year
    evjulday_i = evorigin.julday
    
    ## Now, cut every file.
    