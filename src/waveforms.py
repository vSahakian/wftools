## Function 

#############################################################################
def cut_waveform2event(uncut_file_path,cut_file_path,cut_starttime,cut_endtime,evlon,evlat,evdepth,evid,evorigin,evmag):
    '''
    Cut a waveform into an event file
    Input:
        uncut_file_path:            String with path to the uncut file (mseed or sac)
        cut_file_path:              String with path to the cut file (mseed or sac)
        cut_starttime:              UTCDateTime of start time for file
        cut_endtime:                UTCDateTime of end time for file
        evlon:                      Event longitude
        evlat:                      Event latitude
        evdepth:                    Event depth
        evid:                       Event id, float, no network code
        evorigin:                   UTCDateTime of event origin
        evmag:                      Event magnitude
    Output:
        Writes cut sac file to cut_file_path             
    '''
    
    from obspy import read
    
    # Read in mseed data:
    mseedst = read(uncut_file_path)
    print uncut_file_path
    
    # Cut the data, for all traces in the stream:
    mseedst.slice(starttime=cut_starttime,endtime=cut_endtime)
    print cut_starttime
    print cut_endtime
    print mseedst
    
    # Write to the output file, in sac...
    mseedst.write(cut_file_path,format='SAC')
    
    # Reread it in, as sac, to add the header info:
    sacst = read(cut_file_path)
    
    # Write sac header:
    for tracei in range(len(sacst)):
        sacst[tracei].stats['sac']['evlo'] = evlon
        sacst[tracei].stats['sac']['evla'] = evlat
        sacst[tracei].stats['sac']['evdp'] = evdepth
        sacst[tracei].stats['sac']['nevid'] = evid
        sacst[tracei].stats['sac']['o'] = evorigin
        sacst[tracei].stats['sac']['mag'] = evmag
        
        print sacst[tracei].stats
        
    sacst.write(cut_file_path,format='SAC')
    
    
    


#############################################################################
def download_response(network,station,location,channel,start,end,respfile):
    '''
    Download instrument response file from IRIS and save to .resp
    Input:
        network:            String with network name
        station:            String with station name
        location:           String with location - can have * for wildcards
        channel:            String with channel - can have * for wildcards
        start:              String with start date and time: yyy-mm-ddThh:mm.sss
        end:                String with end date and time: yyy-mm-ddThh:mm.sss
    Output: 
        respfile:           Prints instrument response to respfile
    '''
    
    from obspy.clients.iris import Client
    from obspy import UTCDateTime
    
    # Set up client
    client = Client()
    
    # Define start and end date for resp file
    startdt = UTCDateTime(start)
    enddt = UTCDateTime(end)
    
    # Download resp data
    dlstring = 'downloading resp data for network ' + network + ', station ' \
        + station + ', location and channel ' + location + ' ' + channel \
        + ', \n for time ' + start + ' to ' + end
    print dlstring
        
    respdata = client.resp(network,station,location,channel,starttime=startdt,endtime=enddt)
    
    # Save to file:
    respf = open(respfile,'w')
    respf.write(respdata)
    respf.close()
    
    # Print statement:
    print 'Saved resp to file ' + respfile


#############################################################################

def remove_response(uncorrected_sac_file,resp_file,corrected_sac_file,water_level_bds,resp_unit):
    '''
    Remove the instrument response from a record, given a sac and resp file
    Input:
        uncorrected_sac_file:           String with path to the recording in sac
        resp_file:                      String with path to response file directory
        corrected_sac_file:             String with path to output corrected files directory
        water_level_bds:                Water level filter bounds (0min, ramp min, ramp max, 0max)
        resp_unit:                      String with unit of resp: 'DISP', 'VEL', or 'ACC'
    '''
    
    from obspy import read
    import matplotlib.pyplot as plt
    from os import path

    ######
    ## Read file - this puts it into a "stream object" (named st here):
    
    st = read(uncorrected_sac_file)
    
    # Get times and raw data:
    times_raw = st[0].times()
    amplitude_raw = st[0].data
    
    ######
    ## Remove instrument response
    ## Make response:
    seed_response = {'filename': resp_file, 'units': resp_unit}
    
    # Make a copy of the data and save it to original, since the next steps
    #   will alter the data:
    st_orig = st.copy()
    
    # Remove:
    st[0].simulate(paz_remove=None,pre_filt=water_level_bds,seedresp=seed_response)
        
    ######
    ## Write to a sac file
    st.write(corrected_sac_file, format='SAC')
    


#############################################################################

def batch_remove_response(sac_file,resp_dir,out_dir,fig_dir,water_level_bds):
    '''
    Remove the instrument response from a record, given a directory of resp
    files with set filenames: 'RESP.station.network..channel'
    Input:
        sac_file:           String with path to the recording in sac
        resp_dir:           String with path to response file directory
        out_dir:            String with path to output corrected files directory
        fig_dir:            String with path to figure directory
        water_level_bds:    Water level filter bounds (0min, ramp min, ramp max, 0max)
    '''
    
    from obspy import read
    import matplotlib.pyplot as plt
    from os import path
    
    
    
    ###
    ## Get station/component name for resp file and output file
    # Get the "basename" - the filename itself without extension
    #     path.basename gets the basename with extension; .split('.sac') splits 
    #     this basename into the part before '.sac', and the part after (nothing)
    #     Then take the first part of this (before '.sac') to be the basename
    
    basename = path.basename(sac_file).split('.sac')[0]
    
    # The network is the second part of this, after the number (index 1), station third part, channel fourth
    network = basename.split('.')[1]
    station = basename.split('.')[2]
    channel = basename.split('.')[3]
    
    # Path to response file:
    respfile = resp_dir + 'RESP.' + station + '.' + network + '..' + channel
    
    # Path to output sac file:
    outsacfile = out_dir + basename + '.sac'
    
    
    ########################################
    ######
    ## Read file - this puts it into a "stream object" (named st here):
    
    st = read(sac_file)
    
    # Get times and raw data:
    times_raw = st[0].times()
    amplitude_raw = st[0].data
    
    ## Start plot that will be used for raw and filtered:
    f1, (rawax, filtax)= plt.subplots(2,1,sharex=True)
    
    # Plot raw data:
    rawax.plot(times_raw,amplitude_raw,label='Raw')
    
    
    ######
    ## Remove instrument response
    ## Make response:
    seed_response = {'filename': respfile, 'units': 'DIS'}
    
    # Make a copy of the data and save it to original, since the next steps
    #   will alter the data:
    st_orig = st.copy()
    
    # Remove:
    st[0].simulate(paz_remove=None,pre_filt=water_level_bds,seedresp=seed_response)
        
    ######
    ## Write to a sac file
    st.write(outsacfile, format='SAC')
    
    
    ######
    # Plot corrected data:
    filtax.plot(st[0].times(),st[0].data,label='Corrected')
    
    # Set plot labels:
    filtax.set_ylabel('Amplitude')
    filtax.set_xlabel('Time')
    
    filtax.legend()
    rawax.legend()
    
    rawax.set_title('Raw data and instrument-corrected data\n' + station + '\t' + channel)

    # Save and return figure
    figpath = fig_dir + basename + '.png'
    f1.savefig(figpath)
    
    return f1 
    
    
##############################################################################
#class scsn_catalog:
#    '''
#    '''
#    
#    def __init__(self,eventid,eventorigin,evlat,evlon,evdepth,author,catalog,contrid,mtype,mag,mauthor,evlocation):
#        '''
#        Initiate SCSN catalog 
#        Input:
#            eventid:                Array of integers with event id
#            eventorigin:            Array of strings with event origin time
#            evlat:                  Array with event lat
#            evlon:                  Array with event lon
#            evdepth:                Array with event depth
#            author:                 Array with string of author of event
#            catalog:                Array with string of catalog it belongs to
#            contrid:                Array with string of contributor ID
#            mtype:                  Array with string of magnitude type
#            mag:                    Array with magnitude
#            mauthor:                Array with string of magnitude author
#            evlocation:             Array with string of event location name
#        '''
#        
#        self.eventid = eventid
#        self.eventorigin = eventorigin
#        self.evlat = evlat
#        self.evlon = evlon
#        self.evdepth = evdepth
#        self.author = author
#        self.catalog = catalog
#        self.contrid = contrid
#        self.mtype = mtype
#        self.mag = mag
#        self.mauthor = mauthor
#        self.evlocation = evlocation
#        
#
##############################################################################
#def read_scsn_catalog(catalog_file):
#    '''
#    Read a SCSN catalog, put it into an event catalog class 
#    Input:
#        catalog_file:               String with path to the SCSN event catalog
#    '''
#    import numpy as np
#    
#    #### Read in the data
#    ## Import:
#    
#    eventid_string = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=0,dtype='S')
#    eventorigin = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=1,dtype='S')  
#    evlat = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=2)
#    evlon = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=3)
#    evdepth = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=4)
#    author = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=5,dtype='S')
#    catalog =np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=6,dtype='S')
#    contrid = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=7,dtype='S')
#    mtype = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=9,dtype='S')
#    mag = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=10)
#    mauthor = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=11,dtype='S')
#    evlocation = np.genfromtxt(catalog_file,delimiter='|',skip_header=1,usecols=12,dtype='S')
#        
#    # Convert eventid_string to a float:
#    eventid = np.zeros(len(eventid_string))
#    
#    for eventi in range(len(eventid_string)):
#        eventid_i = eventid_string[eventi].split('ci')[1]
#        eventid[eventi] = eventid_i
#        
#    # Turn it into an array of integers instead of floats:
#    eventid = eventid.astype('int')
#    
#    # Put into an scsn catalog class:
#    scsncatalog = scsn_catalog(eventid,eventorigin,evlat,evlon,evdepth,author,contrid,mtype,mag,mauthor,evlocation)
#    
#    # Return the object:
#    return scsncatalog
#    