#### 
# Test waveforms.py to download resp file and use it to remove response
# VJS 6/2017
###

import waveforms as wf

######

network = 'AZ'
station = 'BZN'
location = '*'
channel = 'BH*'

starttime = '1998-01-01T00:00.000'
endtime = '2599-12-31T23:59.000'

prefilt = (0.6,0.9,40,60)

sacfile = '/Users/vsahakian/iris/play_data/cut_sac_files/11034469.AZ.BZN.BHE.sac'
respfile = 'test.resp'
icorr_sacfile = 'test.sac'


#######

# Get response file:
wf.download_response(network,station,location,channel,starttime,endtime,respfile)


# Correct file:
wf.remove_response(sacfile,respfile,icorr_sacfile,prefilt)
