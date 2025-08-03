#!/usr/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs
import sqlite3
import folium

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
        print (records)
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
                longsm = [row[9]], 
                latgsm = [row[10]],
                accuracygsm = [row[11]],
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
    try:
        sqliteConnection = sqlite3.connect('mydatabase.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")  

        sqlite_select_query="select * from positions"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()

        cursor.close()
        return records
    except sqlite3.Error as error:
        print ("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

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
            longsm REAL, 
            latgsm REAL,
            accuracygsm REAL )"""
        cursor.execute(sqlite_create_table_query)
        sqliteConnection.commit()
        print("SQLite table created")

        sqlite_insert_query = "INSERT INTO positions (chipid, date, time, bat, lat, lon, speed, accuracy, longsm, latgsm, accuracygsm)  VALUES ('"
        sqlite_insert_query += input_dict['chipid'][0] + "','"
        sqlite_insert_query += input_dict['date'][0] + "','"
        sqlite_insert_query += input_dict['time'][0] + "',"
        sqlite_insert_query += input_dict['bat'][0] + ","
        sqlite_insert_query += input_dict['lat'][0] + ","
        sqlite_insert_query += input_dict['lon'][0] + ","
        sqlite_insert_query += input_dict['speed'][0] + ","
        sqlite_insert_query += input_dict['accuracy'][0] + ","
        sqlite_insert_query += input_dict['longsm'][0] + ","
        sqlite_insert_query += input_dict['latgsm'][0] + ","    
        sqlite_insert_query += input_dict['accuracygsm'][0] + ")"   

        print (sqlite_insert_query) ; 
        
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

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print ("MY SERVER: I got a GET request.")
        qs = {}
        path = self.path
        parsed = urlparse(path)
        print (parsed)
        get_data_dict = parse_qs(parsed.query)

        print (parsed.path)
        if parsed.path.lower() == "/api/v1/record":
            saveDataDb (get_data_dict)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Get Data')
            with open("test.txt", "a") as myfile:
                myfile.write(self.path+"\r\n")
        elif parsed.path.lower() == "/api/v1/getall":
            data = readAllDataDb()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            print(str(data))
            self.wfile.write(bytes(str(data), 'UTF-8'))
        elif parsed.path.lower() == "/":
            data = readLastDataDb(10)
            firstdata = data[0]
            lat = firstdata['lat'][0]

            lat = firstdata['lat'][0]
            lon = firstdata['lon'][0]
            latgsm = firstdata['latgsm'][0]
            longsm = firstdata['longsm'][0]

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

 
            if (lat != 0  and lon != 0):
                print ("position gps found")
                position = (lat, lon)
                folium.Marker(
                    location=position,
                    tooltip="Click me!",
                    popup="Last position\r\n" + firstdata['date'][0]+' '+firstdata['time'][0],
                    icon=folium.Icon(color="blue"),
                ).add_to(map)
            else:
                position = (latgsm, longsm)
                kw = {"prefix": "fa", "color": "blue", "icon": "tower-broadcast"}
                angle = 0
                icon = folium.Icon(angle=angle, **kw)
                folium.Marker(
                    location=position,
                    tooltip="Click me!",
                    popup="Last position\r\n" + firstdata['date'][0]+' '+firstdata['time'][0],
                    icon=icon
                ).add_to(map)
            
            if (latgsm != 0  and longsm != 0):
                print ("position gps found")
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



            map.save("map.html")

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            print(str(data))
            with open('map.html', 'rb') as file: 
                self.wfile.write(file.read()) # Read the file and send the contents 
        else :
            self.send_response(200)
            self.end_headers()


    def do_POST(self):
        print ("MY SERVER: I got a POST request.")
        print (self.path) 
        if self.path.lower() == "/api/v1/record":
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            post_data_str = post_data_bytes.decode("UTF-8")

            qs = {}
            post_data_dict = parse_qs (post_data_str)
            saveDataDb (post_data_dict)
        
            print (post_data_dict)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Post Data')
            

        elif parsed.path.lower() == "/api/v1/getall":    
            data = readAllDataDb()
            self.send_response(200)
            self.end_headers()
            self.send_header('Content-type', 'text/plain')
            self.wfile.write(bytes(str(data), 'UTF-8'))
            
        else :
            self.send_response(200)
            self.end_headers()

httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
