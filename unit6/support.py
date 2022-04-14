
# coding: utf-8

# ## Module file with support functions for the GHCN station data
# 
# This is not a notebook format file. Instead it contains only Python code. 
# Make sure this file has the extension .py
# 
# 

# In[2]:


"""Support module for working with GHCN data:

# Defined functions:
# ------------------
#\t(1)get_station_monthly: 
#\t\t request a station time series
#\t\t from the Applied Climate Information System
#\t\t http://www.rcc-acis.org/index.html
#\t(2)read_station_list:
#\t\t support function that reads a local text file with
#\t\t all GHCN stations in state of NY
#\t\t The local file needed is expected to be located in
#\t\t the folder ../data (if you are working with notebooks in a subfolder)
#\t\t You can adjust the folder location to your needs with help of 
#\t\t keyword parameters in function calls

# Author: OET
# Note: Code designed for ATM315/ENV315 Python introduction
#
# Version: 1.1
#
# History: 
# 
#\t2022-04-14 
#\t\t Module functions now make use of Pandas DataFrames 
#\t\t Updated the function get_station_list() to allow updating the local directory
#\t\t where the station list file is located.
#
#\t\t Renamed the function to read_station_list()
"""

import numpy as np
import matplotlib.pyplot as plt
import urllib3
import json
import datetime as dt
import pandas as pd

#########################################################################################################
# function that reads the GHCN station list on the FTP server site
# and returns a list with all US stations
#########################################################################################################

def read_station_list(sid_code="USW",file_name='ghcnd_stations_NY.txt',path_name='../data/'):
    """Reads the local text file with GHNC station id information
    
    The example file is named ghcnd_stations_NY.txt. The list is filtered for 
    stations with specific strings in the station ID lables. It finds 
    stations with station identifier starting with specific string.
    
    Parameters:
    -----------
        sid_code: string
            A keyword parameter that can be changed to work with other country
            or other station id types (e.g. 'USC'). Default is 'USW'.
        filename: string (optional)
            use this keyword parameter to change the file name string
            (default 'ghcnd_stations_NY.txt')
        pathname: string (optional)
            use this keyword parameter to change the default directory name 
            Use "./" or "" for the current directory (default '../data/')
        
    Returns:
    --------
        A Pandas DataFrame oject with columns
            sid, lat,lon,elev, station_name
    """
    sid,station_name, state = [],[],[]
    lat,lon,elev = [],[],[]
    print (f"finding all stations in file {path_name+file_name}")
    print (f"with station identifier string starting with '{sid_code}'")
    # this code should be the safer option of dealing with files
    # using the 'with' statement
    with open(path_name+file_name,'r') as f:
        for line in f:
            values=line.split() # use spaces to separate 
            s=values[0]
            if s[0:3]==sid_code: # when matching string in the beginning of station id
                sid.append(s)
                lat.append(np.float(values[1]))
                lon.append(np.float(values[2]))
                elev.append(np.float(values[3]))
                state.append(values[4])
                name=""
                for s in values[5:]:
                    name=name+" "+s
                station_name.append(name)
                #print("%11s %8.4f %8.4f %7.1f %s" %                (sid[-1],lat[-1],lon[-1],elev[-1],station_name[-1]))
        #print (60*"-")
        df=pd.DataFrame({'sid':sid,'lat':lat,'lon':lon,'elev':elev,'station_name':station_name})
    return df
    
#########################################################################################################
# function to get the monthly data from the server
#########################################################################################################
def get_stationdata_monthly(sid,var='avgt',startyear=2017,endyear=2017):
    """Sends request to regional climate center ACIS and gets monthly data for one station.
    Parameters: 
    -----------------
        sid: string 
            a station id
        var: string 
            a variable name (e.g. 'avgt', 'mint', 'maxt')
    Keyword parameters:
    -------------------
        startyear: int    
        endyear: int
            for selecting the year range e.g. 1950 and 2017
    
    Returns:
    --------
        x: list 
            with dates (datetime objects)
        y: list
            with the data (e.g. temperature)
    """ 
    # the http address of the data server
    host="http://data.rcc-acis.org/StnData"
    # forming the query string for the host server
    sdate='&sdate='+str(startyear)+'-01-1'
    edate='&edate='+str(endyear)+'-12-31'
    query='?sid='+sid+'&'+sdate+'&'+edate+'&interval=mly&'    +'elems='+"mly_mean_"+var
    # try to connect and to get the requested data
    # in format ready to export to a csv file
    print (">send data request to "+host+query)
    print ("station id:",sid)
    print ("year range: %4d - %4d" % (startyear,endyear))
    print ("> still waiting for response ...")
    try:
        http= urllib3.PoolManager()
        response = http.request('GET',host+query)
        # convert json-string into dictionary
        content =  json.loads(response.data.decode('utf-8'))
        time=[]
        year=[]
        month=[]
        value=[]
        if ('data' in content.keys()):
            meta=content['meta']
            data=content['data']
            for item in data:
                #print (item)
                time.append(dt.datetime.strptime(item[0]+'-01',"%Y-%m-%d"))
                year.append(int(item[0][:4]))
                month.append(int(item[0][5:7]))
                if (item[1]!='M'):
                    value.append(float(item[1]))
                else:
                    value.append(np.NAN)
        else:
            time=[]
            value=[]
            year =[]
            month =[]
    except Exception as e:
        print ("error occurred:", e)
        time= []
        value= []
        year = []
        month = []
        return
    print(">... done")
    df=pd.DataFrame({'time':time,'year':year,'month':month,var:value}) # var is a string
    df=df.set_index('time')
    return df

