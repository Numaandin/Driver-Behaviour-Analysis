# conda install -c conda-forge cassandra-driver
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians, acos
import json
# =============================================================================
# from cassandra.cluster import Cluster
# =============================================================================
import warnings
warnings.filterwarnings("ignore")
yesterday = dt.date.today() - dt.timedelta(1)
t = (yesterday - dt.date(1970, 1, 1)).total_seconds()
FMT = '%Y-%m-%d %H:%M:%S'
#data = pd.read_csv(r'C:\Users\INFO-DSK-04\Downloads\cassandra_data_20_11-2019.csv')


# =============================================================================
# imei=('911615400067990','861359036048302','861359036046330','869867030115077','869867030123980','869867030133294','869867030717930','869867030740296','869867030740858','869867030759999','869867030760005','869867030129649','869867030138533','869867030716288','869867030723334','869867030737730','869867030737995')
# 
# 
# def execute_query(imei=[]): #Give input imei's in a list
#     query = "select *from devicedata where imei In "+ str(imei) +" and devicetime>=" + str(int(t)) +" and devicetime<=" + str(int(t+86399))+"  ALLOW FILTERING;"
#     print(str(imei))
#     #print('Connecting to server...')
#     cluster = Cluster(['45.114.143.13'])
#     session = cluster.connect('assettl_tma')
#     #print("--- %s seconds ---" % (time.time() - start_time))
#     #print('Importing the data...')
#     data = pd.DataFrame(list(session.execute(query)))
#     session.shutdown()
#     return(data)
# 
# execute_query(imei)
# =============================================================================

# =============================================================================
# Function angle_between_vectors_degrees
# =============================================================================
def angle_between_vectors_degrees(u, v):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    return np.degrees(
        acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))

# =============================================================================
# Function for preprocessing data
# =============================================================================
def preprocessing(tasks):
#     print('Data Preprocessing...')
    lat=[]
    long=[]
    spd=[]
    for t in tasks:
        la = json.loads(t.get("devicedata"))['dvd'][0]['ldt'][0]['lat']
        lo = json.loads(t.get("devicedata"))['dvd'][0]['ldt'][0]['lon']
        sp = json.loads(t.get("devicedata"))['dvd'][0]['ldt'][0]['spd']

        lat.append(float(la))
        long.append(float(lo))
        spd.append(float(sp))
        
    tasks=pd.DataFrame(tasks)
    tasks['Latitude'] = lat
    tasks['Longitude'] = long
    tasks['Speed'] = spd

    tasks['Latitude'] = tasks['Latitude'].astype(float)
    tasks['Longitude'] = tasks['Longitude'].astype(float)
    tasks['Speed'] = tasks['Speed'].astype(int)
    
    dt = []
    for i in tasks.devicetime:
        dt.append(datetime.fromtimestamp(i))   
    tasks['TrackDateTime'] = dt

    tasks=tasks[['imei', 'Latitude', 'Longitude', 'Speed','TrackDateTime']]
    print(tasks)
    return tasks



# =============================================================================
# Creating angle Column
# =============================================================================
def angle(df):
    angle1 = [0]
    for i in range(1,len(df),1):   
        if i != len(df['Latitude'])-1:
            # The points in tuple Latitude/Longitude degrees space
            A = [df.Latitude.iloc[i-1],df.Longitude.iloc[i-1]]
            B = [df.Latitude.iloc[i],df.Longitude.iloc[i]]
            C = [df.Latitude.iloc[i+1],df.Longitude.iloc[i+1]]
            try:
                if A == B == C:
                    angle1.append(0)

                elif ((A==B) | (B==C)):
                    angle1.append(0)

                else:
                    # Convert the points to numpy Latitudeitude/Longitudegitude radians space
                    a = np.radians(np.array(A))
                    b = np.radians(np.array(B))
                    c = np.radians(np.array(C))

                    # print(a,'\n',b,'\n',c,'\n\n')

                    # Vectors in Latitudeitude/Longitudegitude space
                    avec = a - b
                    cvec = c - b

                    # Adjust vectors for changed Longitudegitude scale at given Latitudeitude into 2D space
                    lat_ = b[0]
                    avec[1] *= cos(lat_)
                    cvec[1] *= cos(lat_)

                    # Find the angle between the vectors in 2D space
                    angle2deg = angle_between_vectors_degrees(avec, cvec)
                    angle1.append(angle2deg)

            except:
                angle1.append(0)
        else:
            angle1.append(0)
    return(angle1)
    #df['Angle'] = angle1
            

# =============================================================================
# Creating suuden_acc Column
# =============================================================================
def rapid_acc(df):
    sudden_acc= [0]
    ra=[0]
    for i in range(1, len(df), 1):    
        x = int((datetime.strptime(str(df.TrackDateTime.iloc[i]), FMT) - datetime.strptime(str(df.TrackDateTime.iloc[i-1]), FMT)).total_seconds())
        y = df.Speed.iloc[i] - df.Speed.iloc[i-1]

        if (((x > 0) & (x < 7)) & (y > 25)):
            sudden_acc.append(15)
            ra.append(3)

        elif (((x > 0) & (x < 62)) & (df['distance'].iloc[i] < 0.03) & (y > 35)):
            sudden_acc.append(15)
            ra.append(3)

        elif (((x > 0) & (x < 12)) & (df['distance'].iloc[i] < 0.04) & (y > 45)):
            sudden_acc.append(15)
            ra.append(3)
            
        elif((df['distance'].iloc[i] < 0.02) & (y > 25)):
            sudden_acc.append(15)
            ra.append(3)
            
        else:
            sudden_acc.append(0)
            ra.append(0)
    return(sudden_acc,ra)

def distance(df):
    R = 6371 # Radius of the earth in km
    dist = [0]
    for i in range(1, len(df.Longitude), 1):
        dLat = radians(df.Latitude.iloc[i] - df.Latitude.iloc[i-1])
        dLon = radians(df.Longitude.iloc[i] - df.Longitude.iloc[i-1])
        rLat1 = radians(df.Latitude.iloc[i-1])
        rLat2 = radians(df.Latitude.iloc[i])
        a = sin(dLat/2) * sin(dLat/2) + cos(rLat1) * cos(rLat2) * sin(dLon/2) * sin(dLon/2) 
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c
        dist.append(d)
    return(dist)
#     df['distance'] = dist

def harshbraking(df):
    harsh_braking = [0]
    hb=[0]
    for i in range(1, len(df), 1):    
        x = int((datetime.strptime(str(df.TrackDateTime.iloc[i]), FMT) - datetime.strptime(str(df.TrackDateTime.iloc[i-1]), FMT)).total_seconds())
        y = df.Speed.iloc[i] - df.Speed.iloc[i-1]

        if (((x > 0) & (x < 7)) & (df['distance'].iloc[i] < 0.012) & (y < -20)):
            harsh_braking.append(14)
            hb.append(3)

        elif (((x > 0) & (x < 7)) & (df['distance'].iloc[i] < 0.027) & (y < -25)):
            harsh_braking.append(14)
            hb.append(3)

        elif (((x > 0) & (x < 7)) & (y < -30)):
            harsh_braking.append(14)
            hb.append(3)

        elif (((x > 0) & (x < 22)) & (df['distance'].iloc[i] < 0.032) & (y < -40)):
            harsh_braking.append(14)
            hb.append(3)

        elif (((x > 0) & (x < 62)) & (df['distance'].iloc[i] < 0.027) & (y < -40)):
            harsh_braking.append(14)
            hb.append(3)

        elif (((x > 0) & (x < 62)) & (df['distance'].iloc[i] < 0.04) & (y < -35) & (df.Speed.iloc[i-1] > 50)):
            harsh_braking.append(14)
            hb.append(3)

        elif  ((df['distance'].iloc[i] < 0.012) & (y < -20)):
            harsh_braking.append(14)
            hb.append(3)

        else:
            harsh_braking.append(0)
            hb.append(0)
    return(harsh_braking,hb)

def rashturn(df):
    rash_turn = [0]
    rt=[0]
    for i in range(1, len(df.Speed), 1):

        x = int((datetime.strptime(str(df.TrackDateTime.iloc[i]), FMT) - datetime.strptime(str(df.TrackDateTime.iloc[i-1]), FMT)).total_seconds())
        if ((x > 0) & (x < 6) & (df['distance'].iloc[i] < 0.02)):        

            if ((df['Angle'].iloc[i] > 30) & (df['Angle'].iloc[i] <= 50) & (df['Speed'].iloc[i] > 10)):            
                rash_turn.append(32)
                rt.append(5)

            elif ((df['Angle'].iloc[i] > 50) & (df['Angle'].iloc[i] <= 90) & (df['Speed'].iloc[i] > 15)):            
                rash_turn.append(32)
                rt.append(5)

            elif ((df['Angle'].iloc[i] > 90) & (df['Angle'].iloc[i] <= 120) & (df['Speed'].iloc[i] > 18)):            
                rash_turn.append(32)
                rt.append(5)

            elif ((df['Angle'].iloc[i] > 120) & (df['Angle'].iloc[i] <= 150) & (df['Speed'].iloc[i] > 25)):            
                rash_turn.append(32)
                rt.append(5)

            elif ((df['Angle'].iloc[i] > 150) & (df['Angle'].iloc[i] <= 160) & (df['Speed'].iloc[i] > 30)):            
                rash_turn.append(32)
                rt.append(5)


            elif ((df['Angle'].iloc[i] > 160) & (df['Angle'].iloc[i] <= 170) & (df['Speed'].iloc[i] > 35)):            
                rash_turn.append(32)
                rt.append(5)

            else:
                rash_turn.append(0)
                rt.append(0)

        else:
            rash_turn.append(0)
            rt.append(0)
    return(rash_turn,rt)

def driverscorecard(df):
    ds = []
    for i in range(0, len(df)):
        if i == 0:
            ds.append(100)
        else:
            ds.append(ds[i-1]-df['score'].iloc[i])
    return(ds)
    

def remove_values_from_list(the_list, val):
      return [value for value in the_list if value != val]


# =============================================================================
# Generating Alerts...
# =============================================================================

def generatealerts(data):
    print("Generating")
    all_data = []
    all_imei = data.imei.unique()
    for i in all_imei:
        df = data[data['imei'] == i]

        df['distance'] = distance(df)   
        df['Angle'] = angle(df)  
        
        df['Sudden_Acceleration'],df['ra'] = rapid_acc(df)
        df['Harsh_Braking'], df['hb']= harshbraking(df)
        df['Rash_Turning'], df['rt'] = rashturn(df)
        
    #changing format
        df['Sudden_Acceleration'] = df['Sudden_Acceleration'].astype(int)
        df['Harsh_Braking'] = df['Harsh_Braking'].astype(int)
        df['Rash_Turning'] = df['Rash_Turning'].astype(int)
        df['score']=df[['ra','hb','rt']].sum(axis=1)
        df['Driver_scorecard'] = driverscorecard(df)
        #print("now",df)
        

        all_data.append(df)

    All_Data = pd.concat(all_data)

    Alerts = All_Data[(All_Data['Sudden_Acceleration'] == 15) |
                              (All_Data['Harsh_Braking'] == 14) |
                              (All_Data['Rash_Turning'] == 32)]
    
    Alerts = Alerts[['imei', 'TrackDateTime','Latitude','Longitude','Sudden_Acceleration','Harsh_Braking','Rash_Turning','Driver_scorecard']]
    Alerts = Alerts.reset_index(drop=True)    
    Alerts['Alert_Type']= [(each[4],each[5],each[6]) for each in Alerts.values]
    Alerts['Alert_Type']=[remove_values_from_list(each, 0.0) for each in  Alerts.Alert_Type]
    return(Alerts)
    
def sendalerts(alerts):
    alrt=alerts.to_json(orient='records')
    return(alrt)
# =============================================================================
# Starting process of generating alerts
# =============================================================================
def startprocess(data):
    print('starting preprocess')
    data1=preprocessing(data)
    print("Preprocessing done, Generating alerts now")
    Alerts=generatealerts(data1)
    print("generating alerts done")
    return(Alerts)