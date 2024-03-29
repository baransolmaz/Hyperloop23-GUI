import math
from tkinter import *
from tkinter.ttk import *
import tkinter.scrolledtext as ST
import serial
import time
import threading as thread
import socket
from datetime import datetime
import re
_COM_TYPE_ = 1 # 0 For Lora , 1 For Eth
_END_FLAG_ = 0
_USB_PORT_ = '/dev/ttyUSB0'

_HOST_ = '192.168.9.3'  # The server's hostname or IP address
_PORT_ = 5656  # The port used by the server

_LOG_FILE_NAME_ = datetime.now().strftime("%d.%m.%Y %H:%M:%S") # Get Current Date
open("Logs/"+_LOG_FILE_NAME_+".csv", "x") #Create File

_DIRECTION_=-1

class Dialog:
    def __init__(self,txt):
        self.root = Tk()
        self.root.title("ALFA ETA-H")  
        canvas1 = Canvas(self.root, width=300, height=100,  relief='raised')
        canvas1.pack()

        label1 = Label(self.root, text=txt)
        label1.config(font=('helvetica', 15))
        canvas1.create_window(150, 25, window=label1)

        entry1 = Entry(self.root)
        canvas1.create_window(150, 50, window=entry1)

        def getEntry():
            global _HOST_
            _HOST_ = str(entry1.get())
            if len(_HOST_) <= 0:
                _HOST_ = "-"
            else:
                tpl = _HOST_.split(".")
                if len(tpl) != 4:
                    _HOST_ = "-"

            self.root.destroy()

        button1 = Button(self.root,text='Insert', command=getEntry)
        entry1.bind("<Return>", lambda e: getEntry())
        canvas1.create_window(150, 80, window=button1)

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.root.mainloop()
        
class App:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("800x470")  # Screen Size(yatay x dikey)
        self.window.resizable(0, 0)
        
        if getComType() == 0:
            self.window.title("ALFA ETA-H")  # Pencere ismi
        else:
            self.window.title("ALFA ETA-H "+_HOST_)  # Pencere ismi
            
        self.window.iconname("ALFA ETA-H")
        self.window.config(background="#276FBF")
        photo = PhotoImage(file="Images/logo_black.png")  # app icon
        self.window.iconphoto("false", photo)
    #self.appendFile("Ivme X,Ivme Y,Ivme Z,Konum X,Konum Y,Konum Z,Hiz X,Hiz Y,Hiz Z,PYR 3,Sicaklik 2,Basinc")
        self.appendFile("Zaman(sn),Ivme,Hiz,Konum")
        #
        self.speedometer_X = Speedometer(self, "X", 350, 470, 25)
        self.speedometer_Y = Speedometer(self, "Y", 560, 470, 1)
        self.speedometer_Z = Speedometer(self, "Z", 770, 470, 1)
        #
        self.acceleration_txt = Name_Text(
            self, "Acceleration-m/s^2", 1, 450, 30, 148)
        self.acceleration_X = Acceleration(self, "X", 10, 450, 2.2)
        self.acceleration_Y = Acceleration(self, "Y", 55, 450, 0.1)
        self.acceleration_Z = Acceleration(self, "Z", 100, 450, 0.1)
        #
        self.location_txt = Name_Text(self, "Location (m)", 300, 305, 25, 300)
        self.location_X = Location(self, "X", 350, 360, 186)
        self.location_Y = Location(self, "Y", 550, 360, 0.1)
        self.location_Z = Location(self, "Z", 750, 360, 0.1)
        #
        self.pyr =  PYR(self, 470, 0)#PYR(self, 420, 0)
        #
        self.logo = Logo(self, 440, 75)
        #
        self.log = Log(self, 0, 150)
        #
        self.thermometer1 = ThermoSignal(self, "P1", 10, 0)#ThermoSignal(self, "P1", 25, 0) 
        self.thermometer2 = ThermoSignal(self, "P2", 125, 0)#ThermoSignal(self, "P2", 150, 0)
        #
        self.stop_button = Stop_Button(self, 690, 0)
        self.lev_button = Levitation_Button(self, 690, 105)
        self.impulse_button = Impulse_Button(self, 690, 210)
        
        if getComType()==1:
            self.ip_get_button = IP_Button(self, 220,110,0)
            self.ip_send_button = IP_Button(self,320,110,1)
            self.socket = self.create_socket()
        #
        self.power=Power(self,240,0)
        #
        self.pressure = Pressure(self, 355, 0)  # Pressure(self, 285, 0)
        #
        self.direction = DirectionSwitch(self, 550, 100,0)

        if getComType()==0:
            self.conn =serial.Serial()
            self.readData = thread.Thread(target=self.readAndParseDATA_LORA)
        else:
            self.conn, self.addr = -1, -1
            self.readData = thread.Thread(target=self.readAndParseDATA)
        self.readData.start()
        self.data = ""

    def create_socket(self):
        server_socket = socket.socket()  # get instance
        print(_HOST_)
        # bind host address and port together
        server_socket.bind((_HOST_, _PORT_))
        server_socket.listen(2)
        return server_socket
    def connectUSB(self):
        ser = serial.Serial(
            # Serial Port to read the data from
            port=_USB_PORT_,
            #Rate at which the information is shared to the communication channel
            baudrate=9600,
            #Applying Parity Checking (none in this case)
            parity=serial.PARITY_NONE,
            # Pattern of Bits to be read
            stopbits=serial.STOPBITS_ONE,
            # Total number of bits to be read
            bytesize=serial.EIGHTBITS,
            # Number of serial commands to accept before timing out
            timeout=1
        )
        return ser

    def appendFile(self, recived_data):
        _LOG_FILE_ = open("Logs/"+_LOG_FILE_NAME_+".csv", "a")
        _LOG_FILE_.write(recived_data+"\n")
        _LOG_FILE_.close()

    def readAndParseDATA(self):
        self.socket.settimeout(5)
        while(getFlag() == 0):
            try:
                print("Socket Timeout is 5 sec.")
                print("Waiting for client...")
                self.conn, self.addr = self.socket.accept()  # accept new connection
                print("Connection from: " + str(self.addr))
            except socket.timeout:
                print("\n5 sec. over - No Client")
                print("Checking again...\n")
                time.sleep(1)
                pass
            else:
                while(getFlag() == 0):
                    try:
                        # Eğer gönderemezse(Raspberry bağlantisi kesilirse) exception verir
                        self.conn.sendall(b"ping")
                        time1 = time.time()
                        # eğer gönderebiliyorsa bağlantıda sorun yok demektir.
                        data = self.conn.recv(1024).decode()
                        time2 = time.time()
                        print(time2-time1)
                        if getFlag() != 0:
                            break
                        print("Received Data: " + str(data))
                        self.appendFile(str(data))
                        updateAll(app, data.split(","))
                        pass  # While a devam eder
                    except:
                        print("CONNECTION LOST")
                        break  # while dan cikar tekrar bağlanti bekler

                self.conn.close()  # close the connection
  
    def readAndParseDATA_LORA(self):#LoRa
        while(getFlag() == 0):
            try:
                print("Trying to connect USB Port...")
                self.conn = self.connectUSB()
            except Exception as e :#serial.SerialException:
                print(e)
                # print("Trying again...")
                time.sleep(3)
                pass
            else:
                print("Connected...\n")
                while(getFlag() == 0):
                    data = self.conn.readline()
                    # bufferBytes = self.conn.in_waiting
                    # if bufferBytes:
                    #      data = data + self.conn.read(bufferBytes)
                    print(data)
                    datalist = DecToStringArr(data.decode())
                    print(len(datalist))
                    if len(datalist) == 0:
                       continue
                    print(datalist[0])
                    if getFlag() != 0:
                        break
                    #print("Received Data: "+ " ".join(data))
                    #self.appendFile(str(data))
                    #updateAll(app, data)
        self.conn.close()


def DecToStringArr(arr):
    result=[]
    # arr=arr[:-4]
    # print(arr)
    if len(arr)==0:
        return result
    pattern = re.compile(r"(?<=40)(.*?)(?=41)")
    if chr(int(arr[:2],10))=='(' and chr(int(arr[-2:],10))==')':
        matches = pattern.findall(arr[2:-2])
        for k in matches:
            strV=""
            for i in range(0,len(k),2):
                strV += chr(int(k[i:i+2], 10))
            result.append(strV)
    return result


class DirectionSwitch:
    def __init__(self, obj, _x_, _y_,state):
        global _DIRECTION_
        _DIRECTION_ = state
        self.state=state
        self.canvas = Canvas(
            obj.window, height=50, width=80, background=obj.window["bg"], highlightthickness=0)
        self.direction = [PhotoImage(
            file='Images/i.png'), PhotoImage(file='Images/g.png')]
        self.img=self.canvas.create_image(0, 0, image=self.direction[state], anchor=NW)
        self.canvas.place(x=_x_, y=_y_)
class Name_Text:
    def __init__(self, obj, _str_, _x_, _y_, _height_, _widht_):
        self.txtCanvas = Canvas(
            obj.window, height=_height_, width=_widht_, background=obj.window["bg"], highlightbackground="black", highlightthickness=1)
        self.txtCanvas.place(x=_x_, y=_y_, anchor=NW)
        self.p_txt = self.txtCanvas.create_text(
            _widht_/2, _height_/2, fill="black", text=_str_, font=('Helvetica 12 bold'), anchor=CENTER)

class Logo:
    def __init__(self, obj, _x_, _y_):
        self.logoCanvas = Canvas(
            obj.window, height=100, width=100, background=obj.window["bg"], highlightthickness=0)
        self.photo = PhotoImage(file="Images/logo_blue.png")
        self.logoCanvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.logoCanvas.place(x=_x_, y=_y_)

class PYR:
    def __init__(self, obj, _x_, _y_):
        self.pyrCanvas = Canvas(
            obj.window, height=100, width=200, background=obj.window["bg"], highlightthickness=0)
        self.pyrCanvas.place(x=_x_, y=_y_, anchor=NW)
        self.photo = PhotoImage(file="Images/roll-pitch-yaw.png")
        self.pyrCanvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.p_txt = self.pyrCanvas.create_text(
            100, 20, fill="black", text="Pitch: 0", font=('Helvetica 12 bold'), anchor=NW)
        self.y_txt = self.pyrCanvas.create_text(
            100, 40, fill="black", text="Yaw  : 0", font=('Helvetica 12 bold'), anchor=NW)
        self.r_txt = self.pyrCanvas.create_text(
            100, 60, fill="black", text="Roll  : 0", font=('Helvetica 12 bold'), anchor=NW)

class Power:
    def __init__(self, obj, _x_, _y_):
        self.powerCanvas = Canvas(
            obj.window, height=100, width=120, background=obj.window["bg"], highlightthickness=0)
        self.powerCanvas.place(x=_x_, y=_y_, anchor=NW)
        self.photo = PhotoImage(file="Images/power.png")
        self.powerCanvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.p_txt = self.powerCanvas.create_text(
            60, 80, fill="black", text="0 W", font=('Helvetica 12 bold'), anchor=NW)

class Pressure:
    def __init__(self, obj, _x_, _y_):
        self.pressureCanvas = Canvas(
            obj.window, height=100, width=100, background=obj.window["bg"], highlightthickness=0)
        self.pressureCanvas.place(x=_x_, y=_y_, anchor=NW)
        self.photo = PhotoImage(file="Images/pressure.png")
        self.pressureCanvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.pressureCanvas.create_text(
            85, 95, fill="black", text="Pa", font=('Helvetica 12 bold'))
        self.p_txt = self.pressureCanvas.create_text(
            50, 75, fill="black", text="0", font=('Helvetica 12 bold'))

class Impulse_Button:
    def __init__(self, obj, _x_, _y_):
        self.canvas = Canvas(obj.window, height=100, width=102,
                             background=obj.window["bg"], highlightthickness=0)
        self.photo = PhotoImage(file="Images/impulse.png")
        self.canvas.create_image(2, 2, image=self.photo, anchor=NW)
        self.canvas.create_text(
            51, 35, fill="black", text="Impulse", font=('Helvetica 8 bold'))
        self.canvas.place(x=_x_, y=_y_)

class IP_Button:
    def __init__(self, obj, _x_, _y_,type):
        self.canvas = Canvas(obj.window, height=33, width=75,
                             background=obj.window["bg"], highlightthickness=3)
        self.photos = [PhotoImage(file="Images/get_ip.png"),
                       PhotoImage(file="Images/send_ip.png")]
        self.photo = self.photos[type]
        self.canvas.create_image(3, 3, image=self.photo, anchor=NW)
        self.canvas.place(x=_x_, y=_y_)
class Levitation_Button:
    def __init__(self, obj, _x_, _y_):
        self.canvas = Canvas(obj.window, height=90, width=102,
                             background=obj.window["bg"], highlightthickness=0)
        self.photo = PhotoImage(file="Images/levitation.png")
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.canvas.create_text(
            51, 85, fill="black", text="Levitation", font=('Helvetica 10 bold'))
        self.canvas.place(x=_x_, y=_y_)

class Stop_Button:
    def __init__(self, obj, _x_, _y_):
        self.canvas = Canvas(obj.window, height=100, width=100,
                             background=obj.window["bg"], highlightthickness=0)
        self.photo = PhotoImage(file="Images/stop.png")
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.canvas.place(x=_x_, y=_y_)

class Speedometer:
    def __init__(self, obj, _name_, _x_, _y_, _max_):
        # SPEED Canvas
        self.max_speed = _max_
        self.speedCanvas = Canvas(
            obj.window, height=100, width=200, background=obj.window['bg'], highlightthickness=0)
        self.speedometer = PhotoImage(file='Images/speedometer.png')
        self.speedCanvas.create_image(
            103, 52, image=self.speedometer, anchor=CENTER)
        coord = 2, 200, 200, 2
        self.speedCanvas.create_arc(coord, start=0, extent=180, width=2)
        self.speedCanvas.pack()
        self.speedCanvas.place(x=_x_, y=_y_, anchor=SE)
        # SPEED Arrow
        self.speedArrow = self.speedCanvas.create_line(
            100, 100, 0, 100, arrow=LAST, width=5, fill="blue")
        self.angle = 90
        self.speedTxt = self.speedCanvas.create_text(
            100, 65, fill="black", text="0", font=('Helvetica 20 bold'))
        self.nameTxt = self.speedCanvas.create_text(
            100, 85, fill="black", text=_name_, font=('Helvetica 12 bold'))

class Acceleration:
    def __init__(self, obj, _name_, _x_, _y_, _max_):
        self.max_acc = _max_
        self.accCanvas = Canvas(obj.window, height=150, width=32,
                                background=obj.window['bg'], highlightbackground="black", highlightthickness=1)

        # Acc Level
        self.accLevel = self.accCanvas.create_rectangle(
            0, 120, 33, 120, fill="#A10FF0")  # sol alt,sağ üst
        self.accName = self.accCanvas.create_text(
            16, 140, fill="black", text=_name_, font=('Helvetica 12 bold'))
        self.accLevelTxt = self.accCanvas.create_text(
            16, 110, fill="black", text="0", font=('Helvetica 12 bold'))
        self.accCanvas.place(x=_x_, y=_y_, anchor=SW)
        self.level = 0

class Location:
    def __init__(self, obj, _name_, _x_, _y_, _max_):
        self.max_loc = _max_
        self.locCanvas = Canvas(obj.window, height=30, width=200,
                                background=obj.window['bg'], highlightbackground="black", highlightthickness=1)
        self.locLevel = self.locCanvas.create_rectangle(
            30, 31, 30, 0, fill="#A10FF0")  # sol alt,sağ üst
        self.locName = self.locCanvas.create_text(
            15, 20, fill="black", text=_name_, font=('Helvetica 12 bold'))
        self.locLevelTxt = self.locCanvas.create_text(
            45, 20, fill="black", text="0", font=('Helvetica 16 bold'))
        self.locCanvas.place(x=_x_, y=_y_, anchor=SE)
        self.dist = 0

class ThermoSignal:
    def __init__(self, obj, _name_, _x_, _y_):
        self.thermometer = [PhotoImage(
            file='Images/thermo_ok.png'), PhotoImage(file='Images/thermo_bad.png')]
        self.thermoCanvas = Canvas(
            obj.window, height=100, width=100, background=obj.window["bg"], highlightthickness=0)
        self.img = self.thermoCanvas.create_image(
            0, 0, image=self.thermometer[0], anchor=NW)
        self.thermoCanvas.place(x=_x_, y=_y_, anchor=NW)
        self.thermoTxt = self.thermoCanvas.create_text(
            80, 85, fill="black", text="0", font=('Helvetica 15 bold'))
        self.thermoName = self.thermoCanvas.create_text(
            80, 65, fill="black", text=_name_, font=('Helvetica 15 bold'))

class Log:
    def __init__(self, obj, _x_, _y_):
        self.can = Canvas(obj.window, height=20, width=110,
                          background=obj.window["bg"], highlightthickness=0)
        self.t = self.can.create_text(
            2, 2, fill="black", text="LOGS", font=('Helvetica 15 bold'), anchor=NW)
        self.can.place(x=_x_, y=_y_-20)
        self.log = ST.ScrolledText(
            obj.window, width=76, height=8, state="disabled", background=obj.window["bg"])
        self.log.vbar.configure(bg="black")
        self.log.place(x=_x_, y=_y_)


def exit_func(obj):
    setFlag(1)
    obj.readData.join()
    print("Closing...")
    obj.window.destroy()

def updateLocations(obj, XYZ):
    updateLocation(obj.location_X, XYZ[0])
    updateLocation(obj.location_Y, XYZ[1])
    updateLocation(obj.location_Z, XYZ[2])
    obj.window.update()

def updateLocation(obj, value=0):
    value = float(value)
    if (obj.dist > 0) or (obj.dist < 100):
        obj.locCanvas.delete(obj.locLevelTxt)
        obj.locCanvas.delete(obj.locLevel)

        x = 30 + float(180.0/obj.max_loc)*(value)  # maks a göre oranla
        color = colorPicker(float(180.0/obj.max_loc)*(value))
        obj.locLevel = obj.locCanvas.create_rectangle(
            30, 31, x, 0, fill=color)

        obj.dist = value
        obj.locLevelTxt = obj.locCanvas.create_text(
            80, 20, fill="black", text=str(obj.dist)+" m", font=('Helvetica 16 bold'))

# def changeAcc(obj):
#     for i in range(0, 80):
#         updateAccelerations(obj, [i, i, i])
#     for i in range(80, 40, -1):
#         updateAccelerations(obj, [i, i, i])
#     for i in range(40, 100):
#         updateAccelerations(obj, [i, i, i])
#     for i in range(100, -1, -1):
#         updateAccelerations(obj, [i, i, i])


def updateAccelerations(obj, XYZ):
    updateAcceleration(obj.acceleration_X, XYZ[0])
    updateAcceleration(obj.acceleration_Y, XYZ[1])
    updateAcceleration(obj.acceleration_Z, XYZ[2])
    obj.window.update()


def updateAcceleration(obj, value=0):
    value = float(value)
    if (obj.level > 0) or (obj.level < 100):
        obj.accCanvas.delete(obj.accLevelTxt)
        obj.accCanvas.delete(obj.accLevel)

        x = 60.0 - float((60.0/obj.max_acc)*value)
        color = colorPicker(float((120.0/obj.max_acc)*value))
        obj.accLevel = obj.accCanvas.create_rectangle(
            0, 60, 33, x, fill=color)  # sol alt,sağ üst

        obj.level = value
        obj.accLevelTxt = obj.accCanvas.create_text(
            16, 110, fill="black", text=str(obj.level), font=('Helvetica 12 bold'))

# def changeSpeed(obj):
#     for i in range(0, 80):
#         updateSpeeds(obj, [i, i, i])
#     for i in range(80, 40, -1):
#         updateSpeeds(obj, [i, i, i])
#     for i in range(40, 100):
#         updateSpeeds(obj, [i, i, i])
#     for i in range(100, 0, -1):
#         updateSpeeds(obj, [i, i, i])


def updateSpeeds(obj, XYZ):
    updateSpeed(obj.speedometer_X, XYZ[0])
    updateSpeed(obj.speedometer_Y, XYZ[1])
    updateSpeed(obj.speedometer_Z, XYZ[2])
    obj.window.update()


def updateSpeed(obj, speed=0):
    speed = float(speed)
    if (obj.angle < 270) or (obj.angle > 90):
        obj.angle = 90.0 + float(1800.0/obj.max_speed)*speed/10
        #obj.angle += 1.8
        x = 100 - 100*math.sin(math.radians(obj.angle))
        y = 100 + 100*math.cos(math.radians(obj.angle))
        obj.speedCanvas.delete(obj.speedTxt)
        obj.speedCanvas.delete(obj.speedArrow)
        obj.speedTxt = obj.speedCanvas.create_text(100, 65, fill="black",
                                                   text="{:.2f}".format(speed)+" m/s",
                                                   font=('Helvetica 16 bold'))
        obj.speedArrow = obj.speedCanvas.create_line(
            100, 100, 0 + x, y, arrow=LAST, width=5, fill="blue")

# def changeThermo(obj):
#     for i in range(0, 80):
#         updateThermos(obj, [i, i])
#     for i in range(80, 40, -1):
#         updateThermos(obj, [i, i])
#     for i in range(40, 100):
#         updateThermos(obj, [i, i])
#     for i in range(100, 0, -1):
#         updateThermos(obj, [i, i])


def updateThermos(obj, XY):
    updateThermo(obj.thermometer1, XY[0])
    updateThermo(obj.thermometer2, XY[1])
    obj.window.update()


def updateThermo(obj, val=0):
    val = float(val)
    img = obj.thermometer[0]
    if val > 40:
        img = obj.thermometer[1]
    obj.thermoCanvas.delete(obj.img)
    obj.img = obj.thermoCanvas.create_image(
        0, 0, image=img, anchor=NW)
    obj.thermoCanvas.delete(obj.thermoTxt)
    obj.thermoTxt = obj.thermoCanvas.create_text(
        80, 85, fill="black", text=str(val), font=('Helvetica 15 bold'))

# def changePower(obj):
#     for i in range(0, 80):
#         updatePower(obj.power, i)
#         obj.window.update()
#     for i in range(80, 40, -1):
#         updatePower(obj.power, i)
#         obj.window.update()
#     for i in range(40, 100):
#         updatePower(obj.power, i)
#         obj.window.update()
#     for i in range(100, 0, -1):
#         updatePower(obj.power, i)
#         obj.window.update()


def updatePower(obj, value=0):
    value = float(value)
    obj.powerCanvas.delete(obj.p_txt)
    obj.p_txt = obj.powerCanvas.create_text(
        60, 80, fill="black", text=str(value)+" W", font=('Helvetica 12 bold'), anchor=NW)

# def changePressure(obj):
#     for i in range(0, 80):
#         updatePressure(obj.pressure, i)
#         obj.window.update()
#     for i in range(80, 40, -1):
#         updatePressure(obj.pressure, i)
#         obj.window.update()
#     for i in range(40, 100):
#         updatePressure(obj.pressure, i)
#         obj.window.update()
#     for i in range(100, 0, -1):
#         updatePressure(obj.pressure, i)
#         obj.window.update()


def updatePressure(obj, value=0):
    value = float(value)
    obj.pressureCanvas.delete(obj.p_txt)
    obj.p_txt = obj.pressureCanvas.create_text(
        50, 75, fill="black", text=str(value), font=('Helvetica 12 bold'))

# def changePYR(obj):
#     for i in range(0, 80):
#         updatePYRs(obj, [i, i,i])
#     for i in range(80, 40, -1):
#         updatePYRs(obj, [i, i,i])
#     for i in range(40, 100):
#         updatePYRs(obj, [i, i,i])
#     for i in range(100, 0, -1):
#         updatePYRs(obj, [i, i,i])


def updatePYRs(obj, XYZ):
    updatePYR(obj.pyr, XYZ)
    obj.window.update()


def updatePYR(obj, XYZ):
    obj.pyrCanvas.delete(obj.p_txt)
    obj.pyrCanvas.delete(obj.y_txt)
    obj.pyrCanvas.delete(obj.r_txt)
    obj.p_txt = obj.pyrCanvas.create_text(
        100, 20, fill="black", text="Pitch: "+str(XYZ[0]), font=('Helvetica 12 bold'), anchor=NW)
    obj.y_txt = obj.pyrCanvas.create_text(
        100, 40, fill="black", text="Yaw  : "+str(XYZ[1]), font=('Helvetica 12 bold'), anchor=NW)
    obj.r_txt = obj.pyrCanvas.create_text(
        100, 60, fill="black", text="Roll  : "+str(XYZ[2]), font=('Helvetica 12 bold'), anchor=NW)

# def changeLog(obj):
#     for i in range(0,18000):
#         updateLog(obj.log,str(i))


def updateLog(obj, text):
    obj.log.configure(state="normal")
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S:", t)

    obj.log.insert(INSERT, current_time+" "+str(text) + "\n")
    obj.log.configure(state="disabled")
    obj.log.see(END)


def colorPicker(charge):
    if charge < 20:
        return "#A10000"
    elif charge < 40:
        return "#C25F00"
    elif charge < 60:
        return "#E2BE00"
    elif charge < 80:
        return "#AAB900"
    else:
        return "#71B400"


def getFlag():
    global _END_FLAG_
    return _END_FLAG_


def getComType():
    global _COM_TYPE_
    return _COM_TYPE_

def setFlag(i):
    global _END_FLAG_
    _END_FLAG_ = 1

def set_HOST_(val):
    global _HOST_
    _HOST_ = val

def stop_signal(obj):
    if getComType()==0:
        if obj.conn.is_open:
            obj.conn.write("stop".encode())
            print("STOP")
        else:
            print("No Client")
    else:
        if obj.conn != -1:
            print("STOP")
            obj.conn.send("stop".encode())
        else:
            print("No Client")

def levitation_signal(obj):
    if getComType() == 0:
        if obj.conn.is_open:
            obj.conn.write("levitation".encode())
            print("LEVITATION")
        else:
            print("No Client")
    else:
        if obj.conn != -1:
            print("LEVITATION")
            obj.conn.send("levitation".encode())
        else:
            print("No Client")

def impulse_signal(obj):
    global _DIRECTION_
    #print("IMPULSE,"f'{_DIRECTION_}')
    if getComType() == 0:
        if obj.conn.is_open:
            obj.conn.write("impulse".encode())
            print("IMPULSE'")
        else:
            print("No Client")
    else:
        if obj.conn != -1:
            #global _DIRECTION_
            print("IMPULSE,"f'{_DIRECTION_}')
            obj.conn.send(("impulse,"+f'{_DIRECTION_}').encode())
        else:
            print("No Client")
        
def change_ip_signal(obj):
    if obj.conn != -1:
        print("IP CHANGE => "+_HOST_)
        obj.conn.send(("ip "+_HOST_).encode())
    else:
        print("No Client")

def changeAll(obj):
    for i in range(0, 100):
        updateAll(obj, [i/100, i/1000, i/1000, i+1, i+1, i+1, (i+2) %
                  25, (i+2)/10, (i+2)/10, i+3, i+3, i+3, i+4, i+4, i+4,i/4])

def updateAll(obj, params):
    if getFlag() != 0:
        return
    data = f'{params[0]}'+","+f'{params[6]}'+"," + f'{params[3]}'
    updateLog(obj.log,str(data) )
    obj.appendFile(str(data))
    if getFlag() != 0:
        return
    updateAccelerations(obj, params[0:3])
    if getFlag() != 0:
        return
    updateLocations(obj, params[3:6])
    if getFlag() != 0:
        return
    updateSpeeds(obj, params[6:9])
    if getFlag() != 0:
        return
    updatePYRs(obj, params[9:12])
    if getFlag() != 0:
        return
    updateThermos(obj, params[12:14])
    if getFlag() != 0:
        return
    updatePressure(obj.pressure, params[14])
    updatePower(obj.power, params[15])
    obj.window.update()

def getIP(txt):
    while True:
        set_HOST_("")
        dialog = Dialog(txt)
        dialog.root.mainloop()
        if len(_HOST_) == 0:
            exit()
        else:
            if len(_HOST_) == 1:
                print("Invalid IP...")
                continue
            else:
                break


def getDirection(obj):
    global _DIRECTION_
    if obj.direction.state==0:
        obj.direction.state=1
    else:
        obj.direction.state=0
    _DIRECTION_ = obj.direction.state

    obj.direction.canvas.delete(obj.direction.img)
    obj.direction.img = obj.direction.canvas.create_image(
        0, 0, image=obj.direction.direction[_DIRECTION_], anchor=NW)
        
if __name__ == '__main__':
    if getComType()==1:
        getIP('Insert Your IP:')
    app = App()
    #app.window.bind("<Down>", lambda event, obj=app: changeAll(obj))
    # app.window.bind("<Up>", lambda event, obj=app:changeLoc(obj))
    app.stop_button.canvas.bind(
        "<Button-1>", lambda event, obj=app: stop_signal(obj))
    app.lev_button.canvas.bind(
        "<Button-1>", lambda event, obj=app: levitation_signal(obj))
    app.impulse_button.canvas.bind(
        "<Button-1>", lambda event, obj=app: impulse_signal(obj))
    if getComType()==1:
        app.ip_get_button.canvas.bind(
            "<Button-1>", lambda event, obj=app: getIP("New IP:"))
        app.ip_send_button.canvas.bind(
            "<Button-1>", lambda event, obj=app: change_ip_signal(obj))
        app.direction.canvas.bind(
            "<Button-1>", lambda event, obj=app: getDirection(obj))
    app.window.protocol('WM_DELETE_WINDOW', lambda obj=app: exit_func(obj))
    app.window.mainloop()
