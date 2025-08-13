#!/usr/bin/python3
import sqlite3
import folium
from flask import Flask, request, jsonify , render_template_string
import socket
import base64
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs

import json

app = Flask(__name__)

#Access to Database 

def readLastDataDb(num = 0 ):
    try:
        output_array = []
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")  
        if (num == 0):
            num = 1
        sqlite_select_query="select * from positions order by id desc limit " + str(num)
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for row in records:
            output_dict = dict (
                id = [row[0]], 
                chipid = [row[1]], 
                date = [row[2]], 
                time = [row[3]], 
                bat = [row[4]], 
                lat = [row[5]], 
                lon = [row[6]], 
                speed = [row[7]], 
                accuracy = [row[8]], 
                latgsm = [row[9]], 
                longsm = [row[10]],
                accuracygsm = [row[11]],
                alarmon = [row[12]],
                alarmstatus = [row[13]] ,
                photo = [row[14]] ,

            )
            output_array.append(output_dict)
        cursor.close()
        return output_array
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

def readAllDataDb():
    records = []
    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")  

        sqlite_select_query="select * from positions"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    return records

def ReadDataDb (chipid):
    records = []
    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")  

        sqlite_select_query="select * from positions WHERE 'chipid' = " + chipid
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    
    return records

def ListChipid (chipid):
    records = []

    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")  
        if chipid == "":

            sqlite_select_query="select distinct chipid from positions"
        else:   
            sqlite_select_query="select distinct chipid from positions WHERE chipid = '" + chipid +"'"
        print ("sqlite_select_query : " + sqlite_select_query)
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    output = []
    for row in records:
        print ( "row: " + row[0])
        output.append(row[0])
    return output

def UpdateLastDataDb (img):
    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_update_table_query = "UPDATE positions SET photo = '" + img.decode('utf-8') + "' WHERE id = (SELECT MAX(id) FROM positions)"
        cursor.execute(sqlite_update_table_query)
        sqliteConnection.commit()
        print("Record Updated successfully into sqlite table")
        cursor.close()
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")


def UpdateConfigDb (input):
    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_update_table_query = "UPDATE config SET alarmon = "+ input['alarmon'] + ", SMS = '" + input['SMS'] + "', SMSC = '" + input['SMSC'] +  "', delay = " + input['delay'] +" WHERE chipid = '" + input['chipid'] + "'"
        print ("sqlite_update_table_query : " + sqlite_update_table_query)
        cursor.execute(sqlite_update_table_query)
        sqliteConnection.commit()
        print("Record Updated successfully into sqlite table")

        cursor.close()
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

def ReadConfig (chipid):
    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite for ReadConfig")

        sqlite_create_table_query = """CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chipid TEXT,
            alarmon INTEGER,
            SMS TEXT,
            SMSC TEXT,
            delay INTEGER )"""
        cursor.execute(sqlite_create_table_query)
        sqliteConnection.commit()
        print("SQLite table created config ")
        if chipid == "":
            sqlite_select_query="select * from config"
        else:
            sqlite_select_query="select * from config WHERE chipid = '" + chipid + "'"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        if ((len(records) == 0) and (chipid != "")):
            sqlite_insert_query = "INSERT INTO config (chipid, alarmon, SMS, SMSC, delay)  VALUES ('"
            sqlite_insert_query += chipid + "',"
            sqlite_insert_query += "0"+ ",'"
            sqlite_insert_query += "" + "','"
            sqlite_insert_query += "+33689004000" + "',"
            sqlite_insert_query += "60" + ")"  
            print("sqlite_insert_query : " + sqlite_insert_query) 
            cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            print("SQLite set default config info ")
        if chipid == "":
            sqlite_select_query="select * from config"
        else:
            sqlite_select_query="select * from config WHERE chipid = '" + chipid + "'"
        print ("sqlite_select_query : " + sqlite_select_query)
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    return records

def saveDataDb (input_dict):
    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_create_table_query = """CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            chipid TEXT,
            date TEXT, 
            time TEXT,
            bat REAL,
            lat REAL, 
            lon REAL, 
            speed REAL, 
            accuracy REAL, 
            latgsm REAL,
            longsm REAL, 
            accuracygsm REAL ,
            alarmon INTEGER,
            alarmstatus INTEGER,
            photo TEXT
            )"""
        cursor.execute(sqlite_create_table_query)
        print ("sqlite_create_table_query : " + sqlite_create_table_query)
        sqliteConnection.commit()
        print("SQLite table created")


        sqlite_insert_query = "INSERT INTO positions (chipid, date, time, bat, lat, lon, speed, accuracy, longsm, latgsm, accuracygsm, alarmon, alarmstatus,photo)  VALUES ('"

        sqlite_insert_query += input_dict['chipid'] + "','"
        sqlite_insert_query += input_dict['date'] + "','"
        sqlite_insert_query += input_dict['time']+ "',"
        sqlite_insert_query += input_dict['bat'] + ","
        sqlite_insert_query += input_dict['lat'] + ","
        sqlite_insert_query += input_dict['lon'] + ","
        sqlite_insert_query += input_dict['speed'] + ","
        sqlite_insert_query += input_dict['accuracy'] + ","
        sqlite_insert_query += input_dict['longsm'] + ","
        sqlite_insert_query += input_dict['latgsm'] + ","    
        sqlite_insert_query += input_dict['accuracygsm'] + ","
        sqlite_insert_query += input_dict['alarmon'] + ","
        sqlite_insert_query += input_dict['alarmstatus']+ ","
        if input_dict.get('photo') :
            sqlite_insert_query += input_dict['photo'] + ")"
        else:
            sqlite_insert_query += "''" + ")"
        
        print ("sqlite_insert_query : " + sqlite_insert_query)
        
        cursor.execute(sqlite_insert_query)
        sqliteConnection.commit()
        print("Python Variables inserted successfully into SqliteDb_developers table")

        cursor.close()

    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

#createmap

def createMap(data):
    print ("create map")

    if data:
            
        firstdata = data[0]
        chipid = firstdata['chipid'][0]
        lat = firstdata['lat'][0]
        lon = firstdata['lon'][0]
        latgsm = firstdata['latgsm'][0]
        longsm = firstdata['longsm'][0]

        print ("chipid : " + chipid)
        print ("longitude : " + str (lon))
        print ("latitude : " + str (lat))
        print ("latitude gsm : " + str (latgsm))
        print ("longitude gsm : " + str (longsm))
    
    
        if (lat != 0  and lon != 0):
            position = (lat, lon)
        else:
            position = (latgsm, longsm)
        map = folium.Map(
            location=position,
            zoom_start=15
        )

        accuracy = firstdata['accuracygsm'][0]
        accuracygsm = firstdata['accuracygsm'][0]
        popupcontent = 'Last&nbsp;position\r\n' + firstdata['date'][0]+' '+firstdata['time'][0] 
        popupcontent += '<br><a href="/displaydata?chipid=' + chipid + '"> chipid : ' + chipid + '</a>'
        popupcontent += '<br>bat : ' + str(firstdata['bat'][0])
        if firstdata['photo'][0] != "":
            popupcontent += '<br><img src="data:image/jpeg;base64,' + firstdata['photo'][0] + '" width="200" height="200" alt="photo">'
        if (lat != 0  and lon != 0):
            popupcontent += '<br>lat : ' + str(lat) + '<br>lon : ' + str(lon) + '<br>accuracy : ' + str(accuracy)
            print ("position gps found")
            position = (lat, lon)
            folium.Marker(
                location=position,
                tooltip="Click me!",
                popup=popupcontent,
                icon=folium.Icon(color="blue"),
            ).add_to(map)
        else:
            position = (latgsm, longsm)
            popupcontent += '<br>latgsm : ' + str(latgsm) + '<br>longsm : ' + str(longsm) + '<br>accuracygsm : ' + str(accuracygsm)
            kw = {"prefix": "fa", "color": "blue", "icon": "tower-broadcast"}
            angle = 0
            icon = folium.Icon(angle=angle, **kw)

            folium.Marker(
                location=position,
                tooltip="Click me!",
                popup=popupcontent,
                icon=icon
            ).add_to(map)

        if (latgsm != 0  and longsm != 0):
            print ("position gsm found")
            position = (latgsm, longsm)
            folium.Circle(
                location=position,
                radius=accuracygsm,
                color="blue",
                fill=True,
                fill_opacity=0.2,
                tooltip="GSM Accuracy",
            ).add_to(map)


        lastpoints = []
        for row in data:
            lat = row['lat'][0]
            lon = row['lon'][0]
            latgsm = row['latgsm'][0]
            longsm = row['longsm'][0]
            if (lat != 0  and lon != 0):
                position = (lat, lon)
            else:
                position = (latgsm, longsm)
            lastpoints.append(position)
            folium.PolyLine(lastpoints, tooltip="las position").add_to(map)
    else :
        map = folium.Map(
            zoom_start=15
        )
    return map
#access to Web Server 

@app.route("/")
def fullscreen():
    data = readLastDataDb(10)
  

    map = createMap(data)

    map.get_root().render()
    header = map.get_root().header.render()
    body_html = map.get_root().html.render()
    script = map.get_root().script.render()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    <meta http-equiv="refresh" content="60">
                    {{ header|safe }}
                </head>
                <body>
                    <h1>10 dernieres positions</h1>
                    {{ body_html|safe }}
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
                <script>
                    {{ script|safe }}
                </script>
            </html>
        """,
    
        header=header,
        body_html=body_html,
        script=script,
    )


@app.route("/upload", methods=['POST','GET'])
def upload():
    if request.method == 'GET':
        input_dict = request.args.to_dict()
    if request.method == 'POST':
        input_dict = request.form.to_dict()

    image = request.files['fileToUpload']

    content = image.read() # Get the file contents
    file_name = image.filename # Get the file name
    UpdateLastDataDb(base64.b64encode(content))

    body_html = "Upload data received : " + str(image.filename)
    header = ""
    script = ""

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                </head>
                <body>
                {{ body_html|safe }}

                </body>
                <script>
                    {{ script|safe }}
                </script>
            </html> 

        """,
        body_html=body_html,
        header=header,
        script=script,
    )
@app.route("/updateconfig", methods=['POST','GET'])
def updateconfig():
    if request.method == 'GET':
        input_dict = request.args.to_dict()
    if request.method == 'POST':
        input_dict = request.form.to_dict()

    UpdateConfigDb (input_dict)


    body_html = str(input_dict)
    header = ""
    script = ""

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                    <meta http-equiv="refresh" content="3;URL={{ url_for('display') }}" />
                </head>
                <body>
                {{ body_html|safe }}
                <center>
                You 'll be redirect to {{ url_for('display') }} in 3 seconds
                </center>
                </body>
                <script>
                    {{ script|safe }}
                </script>
            </html> 

        """,
        body_html=body_html,
        header=header,
        script=script,
    )


@app.route("/displaydata", methods=['POST','GET'])
def display():
    if request.method == 'GET':
        input_dict = request.args.to_dict()
    if request.method == 'POST':
        input_dict = request.form.to_dict()

    if 'chipid' in input_dict.keys():
        chipid = input_dict['chipid']
    else:
        chipid = ""
    print  ("chipid : " + chipid)
    resultlistchid = ListChipid ("")
    #readconfig 
    dataconfig = ReadConfig (chipid)

    data = ListChipid (chipid)
    body_html = ""
    header = ""
    script = ""


    return render_template_string(
        """

            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                </head>
                <body>
                    <h1>info device {{ chipid|safe }}</h1>
                    <a href="{{ url_for('fullscreen')}}"><button>Home Page</button></a>
                    <form method="POST" action="{{ url_for('display') }}">
                        <label for="chipid">Choose chipid:</label>
                        <select name="chipid" id="chipid">
                            {%for i in range(0, lenlistchipid)%}
                                <option value="{{listchipid[i]}}">{{listchipid[i]}}</option>
                            {%endfor%}
                        </select>
                        <button type="submit">submit</button>
                    </form>
                    <br>

                    <form method="POST" action="{{ url_for('updateconfig') }}">
                    {%for i in range(0, lendataconfig)%}
                        <table border=2px>
                            <thead>
                                <tr>
                                    <th scope="col">Id</th>
                                    <th scope="col">ChipId</th>
                                    <th scope="col">Alarm on</th>
                                    <th scope="col">SMS</th>
                                    <th scope="col">SMSC</th>
                                    <th scope="col">delay</th>
                                    <th scope="col">Action</th>>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <th scope="row">{{dataconfig[i][0]}}</th>
                                    <td>{{dataconfig[i][1]}}<input type="hidden" id="chipid" name="chipid" value="{{dataconfig[i][1]}}" /></td>
                                    <td><input type="integer" name="alarmon" id="alarmon" value="{{dataconfig[i][2]}}"</td>
                                    <td><input type="text" name="SMS" id="SMS" value="{{dataconfig[i][3]}}"</td>
                                    <td><input type="text" name="SMSC" id="SMSC" value="{{dataconfig[i][4]}}"</td>
                                    <td><input type="integer" name="delay" id="delay" value="{{dataconfig[i][5]}}"</td>

                                    <td><button type="submit">submit</button></td>
                                </tr>
                            </tbody>
                        </table>
                    {%endfor%}
                    </form>
                    {{ body_html|safe }}
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
            </html>
        """,
        listchipid = resultlistchid,
        lenlistchipid = len(resultlistchid),
        dataconfig = dataconfig,
        lendataconfig = len(dataconfig),
        chipid=chipid,
        header=header,
        body_html=body_html,
        script=script,
    )



@app.route("/api/<version>/getall", methods=['POST','GET'])
def getall(version):
    print (version)
    input_dict = request.form.to_dict()
    data = readAllDataDb()

    body_html = str(data)

    return render_template_string(
        """
        {{ body_html|safe }}
        """,
        body_html=body_html,
    )


            
@app.route("/api/<version>/recordset", methods=['POST','GET'])
def record(version):
    print (version)
  
    if request.method == 'GET':
        input_dict = request.args.to_dict()
    if request.method == 'POST':
        input_dict = request.form.to_dict()
    print (request)

    print (input_dict)
    saveDataDb (input_dict)
    return f"record"

@app.route("/api/<version>/configget", methods=['POST','GET'])
def config(version):
    print (version)
 
    input_dict = request.form.to_dict()
    data = ReadConfig (input_dict['chipid'])
    print ("config for  " + input_dict['chipid'])

    if len(data) != 0:
        config = {
	    "id": data[0][0],
	    "chipid": data[0][1],
        "alarmon": data[0][2],
        "SMS": data[0][3],
        "SMSC": data[0][4],
        "delay": data[0][5]
	    }
        body_html = json.dumps(config)
    else:
        body_html = ""


    return render_template_string(
        """
        {{ body_html|safe }}
        """,
        body_html=body_html,
    )


if __name__ == "__main__":
    socket.setdefaulttimeout(60)
    app.run(debug=True,host='0.0.0.0', port=8000)