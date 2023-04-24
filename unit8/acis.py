
# coding: utf-8

# # Getting archived weather data for US station data 
# 
# 
# This script defines a function that downloads daily weather data from weather stations (GHCND).
# The server is at [http://data.rcc-acis.org](http://data.rcc-acis.org)
# Here we retrieve data for one year only.
# 
# Then a function is defined that can read the local data file.
# 
# 

# ## 1 Defining functions 
# 
# There are two tasks we need to take care of: 
# * providing a function that can get the data from the server and save it to a local file
# * a function that can load the data from the created (csv-formatted) file
# 

# ### 1.1 Functions that send request to the host server
# 
# * The host and the database is located and curated at/by the [Applied Climate Information System](http://www.rcc-acis.org/index.html)
# 
# * The specific dataset we access is the Daily Global Historical Climatology Network - Daily
# [see here for information] (ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt)
# 
# * Here we request daily data by sending a request to the host server. It returns data for a single station. The variables are 2m air temperature (min, mean, and daily max value), precipitation, and snow.
# 
# * The script defines two functions:
#      * one is requesting one year of data: *download_stationdata_dly*
#      * the second allows to retrieve a range of years: *download_stationdata_dly_years*
#      
# ---
# 
# NOTE: In principle you use these functions, loop over all stations and get all daily data from around the entire globe (**GBs of data, so don't do it on this Jupyter Hub!**). 
# A list of US stations airport stations (station ids starting with 'USW') you can find in the for example in this list at the [NOAA FTP site ghcnd-stations.txt](ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt).
# 
# ---
# 
# 
# 
# 

# In[1]:


# request a station time series
# from Applied Climate Information System
# http://www.rcc-acis.org/index.html
# Author: OET
# code designed for ATM315/ENV315 Python introduction
import urllib3
import json
import datetime as dt


def download_stationdata_dly(sid,year=1950,
                             with_header=True,
                             with_column_names=True,
                             silent=False):
    """Downloads station weather data (GHCN-daily) from the regional climate center in Cornell.
    and saves it in a local CSV file. One year of data is retrieved.
    
    Note the standard file name used for the created file looks like this:
    'USW0001234_1950_dly.csv'  (sid+'_'+str(year)+'_dly.csv' ).
    This function retrieves three daily temperature values: min, mean, max,
    precipitation, and precipitation in form of snow.

    Input parameter: 
        sid: a string with a station id number
        year: integer number for the year to download (default 1950)
        with_header: logical parameter (default True). 
                     If True 5 header lines are written to output file
        with_column_names: logical parameter (default True).
                     If True the column names are written to the output file
    Returned object:
        content: the downloaded data information (one long string)
    
    Related functions: download_stationdata_dly_years
    """    
    #year=1880 # very few data we have from that far back
    # the http address of the data server
    host="http://data.rcc-acis.org/StnData"
    # forming the query string for the host server
    sdate='&sdate='+str(year)+'-01-1'
    edate='&edate='+str(year)+'-12-31'
    query='?sid='+sid+'&'+sdate+'&'+edate+'&interval=dly&'    +'elems=mint,avgt,maxt,pcpn,snow&output=csv'
    
    # try to connect and to get the requested data
    # in format ready to export to a csv file
    print("#"*80)
    print ("# send data request to "+host)
    print("#"*80)
    column_names=("date","min_temp","mean_temp","max_temp","pcpn","snow")
    try:
        http= urllib3.PoolManager()
        response = http.request('GET',host+query)
        content =  response.data.decode('utf-8')
    except Exception as e:
        print ("error occurred:", e)
        return
    # continue when sucessful data request
    # store in a local file
    # NOTE: one can work directly with the data, of course
    # without saving. But we want to use the np.loadtxt() function
    
    local_file=sid+'_'+str(year)+'_dly.csv'
    fout=open(local_file,'w')
    ihelp=content.find('\n')
    # ihelp is the position in the content string where the first 
    # line ends. That contains the station's name
    station_name=content[:ihelp]
    headerline="# station "+station_name+" data retrieved from "+host
    fout.write(headerline+'\n') #'\n' is the newline special character
    headerline="# at UTC time:"+str(dt.datetime.utcnow())
    fout.write(headerline+'\n')
    headerline="# with query string "+query
    fout.write(headerline+'\n')
    headerline="#using python package "+        urllib3.__name__+' (V'+urllib3.__version__+')'
    fout.write(headerline+'\n')
    line=''
    for name in column_names:
        line=line+name+','
    fout.write(line[:-1]+'\n') # note I remove the extra comma from line
    fout.write("")
    # I don't want the station name line here
    # so I start in the content string in the next line
    fout.write(content[ihelp+1:])
    
    if  not silent:
        print("saved data to local file "+local_file)
        print("data columns are:")
        print("="*20)
        i=0
        line=""
        for col in column_names:
            print (str(i)+" : "+col)
            i=i+1
    return content


#######################################################################################
# this function retrieves data starting from the given start year to end year
#######################################################################################
def download_stationdata_dly_years(sid,startyear=1950,endyear=2017,
                             with_header=True,
                             with_column_names=True,
                             silent=False):
    """Downloads station weather data (daily) from regional climate center in Cornell 
    and saves it in a local CSV file. A range of years is retrieved.
    
    Note the standard file name used for the created file looks like this:
    'USW0001234_1950-2017_dly.csv'  (sid+'_'+str(startyear)+'-'+str(endyear)+'_dly.csv').
    This function retrieves three daily temperature values: min, mean, max,
    precipitation, and precipitation in form of snow.
    
    Input parameter: 
        sid: a string with a station id number
        startyear: integer number for the first year 
        endyear: integer number for the last year
        with_header: logical parameter (default True). 
                     If True 5 header lines are written to output file
        with_column_names: logical parameter (default True).
                     If True the column names are written to the output file
    Returned object:
        content: the downloaded data information (one long string)
        
    Related functions: download_stationdata_dly  
        
    """    
    #startyear=1880  very few data we have from that far back
    # the http address of the data server
    host="http://data.rcc-acis.org/StnData"
    # forming the query string for the host server
    sdate='&sdate='+str(startyear)+'-01-1'
    edate='&edate='+str(endyear)+'-12-31'
    query='?sid='+sid+'&'+sdate+'&'+edate+'&interval=dly&'    +'elems=mint,avgt,maxt,pcpn,snow&output=csv'
    # try to connect and to get the requested data
    # in format ready to export to a csv file
    print("#"*80)
    print ("# send data request to "+host)
    print("#"*80)
    column_names=("date","min_temp","mean_temp","max_temp","pcpn","snow")
    try:
        http= urllib3.PoolManager()
        response = http.request('GET',host+query)
        content =  response.data.decode('utf-8')
    except Exception as e:
        print ("error occurred:", e)
        return
    # continue when sucessful data request
    # store in a local file
    # NOTE: one can work directly with the data, of course
    # without saving. But we want to use the np.loadtxt() function
    
    local_file=sid+'_'+str(startyear)+'-'+str(endyear)+'_dly.csv'
    fout=open(local_file,'w')
    ihelp=content.find('\n')
    # ihelp is the position in the content string where the first 
    # line ends. That contains the station's name
    station_name=content[:ihelp]
    headerline="# station "+station_name+" data retrieved from "+host
    fout.write(headerline+'\n') #'\n' is the newline special character
    headerline="# at UTC time:"+str(dt.datetime.utcnow())
    fout.write(headerline+'\n')
    headerline="# with query string "+query
    fout.write(headerline+'\n')
    headerline="#using python package "+        urllib3.__name__+' (V'+urllib3.__version__+')'
    fout.write(headerline+'\n')
    line=''
    for name in column_names:
        line=line+name+','
    fout.write(line[:-1]+'\n') # note I remove the extra comma from line
    fout.write("")
    # I don't want the station name line here
    # so I start in the content string in the next line
    fout.write(content[ihelp+1:])
    
    if  not silent:
        print("saved data to local file "+local_file)
        print("data columns are:")
        print("="*20)
        i=0
        line=""
        for col in column_names:
            print (str(i)+" : "+col)
            i=i+1
    return content



# ### 1.2 The function that reads the  local file
# 
# In principle one could attempt to read the csv file with the np.loadtxt. The data, however contain some flags 'M' and 'T' for indicating missing values and 'trace of precipition', respectively, and that causes some trouble.
# 
# Note: The format I choose for the downloaded data contains 5 lines of header information. If we used the method for downloading 100 or 1000s of stations and many years, one could update the function and remove the headers, of course. But I want to provide a readable format here for educational purposes.
# The function *load_station_data_dly* returns two objects: 
# 1. a 2-dimensional numpy array (rows: one for each day)
# 2. a list with the names of the columns
# 




import datetime as dt
import numpy as np
import pandas as pd
def load_station_data_dly(filename,skiprows=5,silent=False,fmt='df'):
    """This function reads the downloaded GHCN-daily data from the CSV file line by line
    and converts values in the array:
    'M' -> np.NAN 
    'T' -> 1E-9 (small positive for trace of precip)
    
    Input parameter:
    filename (string) : a string with the file name (including the path)
    Optional input parameter:
    skiprows (integer): number of lines to skip before reading lines with data values
    silent (logical)  : turn on/off the print() statements inside the function
    
    Returns:
    result:       a numpy array with rows for daily data, and columns for date, 
                  and meteorological variables
    column_names: a tuple with the column names (strings).
    
    Related functions: download_stationdata_dly, download_stationdata_dly_years
    """
    column_names=("year","month","day","min_temp","mean_temp","max_temp","pcpn","snow")
    trace_of_pcpn=1E-9
    fin=open(filename,'r')
    i=0
    date=[]
    year=[]
    month=[]
    day=[]
    tmax=[]
    tmin=[]
    tmean=[]
    pcpn=[]
    snow=[]
    n=0
    while n < skiprows:
        next(fin) # go to next line
        n=n+1
    for line in fin:
        #print(line)
        values=line.split(',')    
        d=dt.datetime.strptime(values[0], '%Y-%m-%d')
        date.append(d)
        year.append(d.year)
        month.append(d.month)
        day.append(d.day)
        if (values[1]!="M"):
            tmin.append(float(values[1]))
        else:
            tmin.append(np.NAN)
        
        if values[2]!="M":
            tmean.append(float(values[2]))
        else:
            tmean.append(np.NAN)
        if (values[3]!="M"):
            tmax.append(float(values[3]))
        else:
            tmax.append(np.NAN)
        if (values[4]!="M" and values[4]!="T"):
            pcpn.append(float(values[4]))
        else:
            if values[4]=='T':
                pcpn.append(trace_of_pcpn)  
            else:
                pcpn.append(np.NAN)
        if (values[5]!="M\n" and values[5]!="T\n"):
            snow.append(float(values[5]))
        else:
            if values[5]=='T\n':
                snow.append(trace_of_pcpn)  
            else:
                snow.append(np.NAN)
        i=i+1
    fin.close()
    # convert to numpy arrays
    day=np.array(day,dtype=int)
    month=np.array(month,dtype=int)
    year=np.array(year,dtype=int)
    tmin=np.array(tmin,dtype=float)
    tmax=np.array(tmax,dtype=float)
    tmean=np.array(tmean,dtype=float)
    if not silent:
        print("number of data rows: "+str(i))
        print("returns the 2-d arrays with columns")
        n=0
        for name in column_names:
            print (str(n)+" "+name)
            n=n+1
    result=np.empty(shape=[i,len(column_names)])
    result[:,0]=year
    result[:,1]=month
    result[:,2]=day
    result[:,3]=tmin
    result[:,4]=tmean
    result[:,5]=tmax
    result[:,6]=pcpn
    result[:,7]=snow
    # 2022-04-28 update return as Pandas data frame 
    if fmt=='df':
        dfout=pd.DataFrame({'year':year,'month':month,'day':day,
                            'min_temp':tmin,
                            'mean_temp':tmean,
                            'max_temp':tmax,
                            'pcpn':pcpn,'snow':snow})
        # OET2022-02-24 
        # add date time information for better handling of time series data
        startdate=dt.datetime(year[0],month[0],day[0])
        n=len(year)
        dfout['time']=pd.Series(pd.date_range(startdate, freq="D",periods=n))
        dfout=dfout.set_index('time')
        return dfout
    elif fmt == 'np':
        return result, column_names 
    else:
        return result, column_names
    




