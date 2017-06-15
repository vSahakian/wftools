#### 
# Test waveforms.py to download resp file and use it to remove response
# VJS 6/2017
###

import waveforms as wf

############################################################################

# Set parameters for resp file:
network = 'AZ'
station = 'BZN'
location = '*'
channel = 'BH*'

# Unit for time series?
tsunit = 'VEL'

# Start and end date/time for resp file:
starttime = '1998-01-01T00:00.000'
endtime = '2599-12-31T23:59.000'

# Pre-filter for instrument response correction:
#   The last number should be the nyquist frequency; second to last reduces
#   the filter towards the nyquist; first two are for the "water level"
prefilt = (0.6,0.9,15,20)

# sacfile (uncorrected) path, respfile path, instr. corrected sac file path:
sacfile = '/Users/vsahakian/iris/play_data/cut_sac_files/11034469.AZ.BZN.BHE.sac'
respfile = 'test.resp'
icorr_sacfile = 'test.sac'

############################################################################

# Get response file - downloads data from IRIS and saves to respfile:
wf.download_response(network,station,location,channel,starttime,endtime,respfile)


# Correct file - loads in uncorrected sac file, corrects w/ prefilter data,
#     and removes instrument response - saves corrected to icorr_sacfile:
wf.remove_response(sacfile,respfile,icorr_sacfile,prefilt,tsunit)



### Could batch this - so could do it in two steps:
# 1.   Read in all files you have, and for every station, download a resp file
#       for all HH channels at once (so set location = '*', channel = 'HH*').
#      Set it to save all these to a resp file directory.
#
# 2.   Read in all uncorrected sac files in a directory, loop through and for each
#       one, look in the resp file directory and find the one that corresponds to 
#       your station/instrument in the loop (can use "split" to get this info, I 
#       can help if you want).  Then, use wf.remove_response inside the loop for 
#       each file, save to a directory of corrected sac files. 


