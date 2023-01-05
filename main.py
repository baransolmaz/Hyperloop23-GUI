import math
from tkinter import *
from tkinter.ttk import *
import serial
_PORT_ = '/dev/ttyUSB0'
class App:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("750x700")  # Screen Size(yatay x dikey)
        self.window.resizable(0, 0)
        self.window.title("ALFA ETA-H")  # Pencere ismi
        self.window.iconname("ALFA ETA-H")
        self.window.config(background="#C7EFCF")
        photo = PhotoImage(file="Images/logo_black.png")  # app icon
        self.window.iconphoto("false", photo)
        #
        self.speedometer_X = Speedometer(self,"X",350,700)
        self.speedometer_Y = Speedometer(self,"Y",550,700)
        self.speedometer_Z = Speedometer(self,"Z",750,700)
        #
        self.acceleration_X=Acceleration(self,"X",10,700)
        self.acceleration_Y=Acceleration(self,"Y",50,700)
        self.acceleration_Z=Acceleration(self,"Z",90,700)
        #
        self.location_X = Location(self, "X", 350, 600)
        self.location_Y = Location(self, "Y", 550, 600)
        self.location_Z = Location(self, "Z", 750, 600)
        #
        # self.mainBattery = Battery(self, "Main", 0, 525)
        # x = 80
        # y = 130
        # self.allBatteries = [[0 for j in range(5)] for i in range(4)]
        # for i in range(4):
        #     for j in range(5):
        #         if ((i*5)+j) < 18:
        #             self.allBatteries[i][j] = Battery(
        #                 self, (i*5+j), (x*j)+1, (y*i)+1)
        # self.signals = Signals(self)
        # self.location = Location(self)
        # self.mapThread = thr.Thread(
        #     target=self.location.updateLoc, args=[self, self.location])
        # self.logo = Logo(self)
        # self.steer = Steering(self)
        # self.readData = thr.Thread(target=self.readAndParseDATA)
        # self.readData.start()
        # self.mapThread.start()

    def connectUSB(self):
        ser = serial.Serial(
            # Serial Port to read the data from
            port=_PORT_,
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

    # def readAndParseDATA(self):
    #     while(getFlag() == 0):
    #         try:
    #             self.serialCon = self.connectUSB()
    #         except serial.SerialException:
    #             time.sleep(3)
    #             pass
    #         else:
    #             while(getFlag() == 0):
    #                 x = self.serialCon.readline()
    #                 #print(x)
    #                 datas = str(x).split(":")
    #                 paket = datas[0][2:4]
    #                 if paket == '1':  # Battery 0 - 12
    #                     paket1(self, datas[1])
    #                 # Battery 12 - 18  + Left -Right Signal +Motor +Leakage Signal+Amper+Volt+pil Temp.
    #                 if paket == '2':
    #                     paket2(self, datas[1])
    #                 if paket == '3':  # direksiyon + konum
    #                     paket3(self, datas[1])
    #             self.serialCon.close()

class Speedometer:
    def __init__(self, obj,_name_,_x_,_y_):
        #SPEED Canvas
        self.speedCanvas = Canvas(
            obj.window, height=100, width=200, background=obj.window['bg'], highlightthickness=0)
        self.speedometer = PhotoImage(file='Images/speedometer.png')
        self.speedCanvas.create_image(103, 52, image=self.speedometer, anchor=CENTER)
        coord = 2, 200, 200, 2
        self.speedCanvas.create_arc(coord, start=0, extent=180, width=2)
        self.speedCanvas.pack()
        self.speedCanvas.place(x=_x_, y=_y_, anchor=SE)
        #SPEED Arrow
        self.speedArrow = self.speedCanvas.create_line(
            100, 100, 0, 100, arrow=LAST, width=5, fill="blue")
        self.angle = 90
        self.speedTxt = self.speedCanvas.create_text(
            100, 65, fill="black", text="0", font=('Helvetica 20 bold'))
        self.nameTxt = self.speedCanvas.create_text(
            100, 85, fill="black", text=_name_, font=('Helvetica 12 bold'))

class Acceleration:
    def __init__(self, obj, _name_, _x_, _y_):
        self.accCanvas = Canvas(obj.window, height=150, width=30,
                                background=obj.window['bg'],highlightbackground="black", highlightthickness=2)
        #Acc Level
        self.accLevel = self.accCanvas.create_rectangle(0,120,31,120, fill="#A10FF0")#sol alt,sağ üst
        self.accName = self.accCanvas.create_text(
            16, 140, fill="black", text=_name_, font=('Helvetica 12 bold'))
        self.accLevelTxt = self.accCanvas.create_text(
            16, 110, fill="black", text="0", font=('Helvetica 16 bold'))
        self.accCanvas.place(x=_x_, y=_y_,anchor=SW)
        self.level = 0

class Location:
    def __init__(self, obj, _name_, _x_, _y_):
        self.locCanvas = Canvas(obj.window, height=30, width=200,
                                background=obj.window['bg'], highlightbackground="black", highlightthickness=2)
        self.locLevel = self.locCanvas.create_rectangle(
            30,31, 30,0, fill="#A10FF0")  # sol alt,sağ üst
        self.locName = self.locCanvas.create_text(
            15, 20, fill="black", text=_name_, font=('Helvetica 12 bold'))
        self.locLevelTxt = self.locCanvas.create_text(
            45, 20, fill="black", text="0", font=('Helvetica 16 bold'))
        self.locCanvas.place(x=_x_, y=_y_, anchor=SE)
        self.dist = 0
        
def exit_func(obj):
    #setFlag(1)
    #obj.readData.join()
    #obj.mapThread.join()
    obj.window.destroy()


def changeLoc(obj):
    for i in range(0, 80):
        updateLocations(obj, [i, i, i])
    for i in range(80, 40, -1):
        updateLocations(obj, [i, i, i])
    #obj.window.update()
    for i in range(40, 100):
        updateLocations(obj, [i, i, i])
    for i in range(100, -1, -1):
        updateLocations(obj, [i, i, i])

def updateLocations(obj, XYZ):
    updateLocation(obj.location_X, XYZ[0])
    updateLocation(obj.location_Y, XYZ[1])
    updateLocation(obj.location_Z, XYZ[2])
    obj.window.update()


def updateLocation(obj, value=0):
    if (obj.dist > 0) or (obj.dist < 100):
        obj.locCanvas.delete(obj.locLevelTxt)
        obj.locCanvas.delete(obj.locLevel)

        x = 30 + int(value*1.04)
        color = colorPicker(value)
        obj.locLevel = obj.locCanvas.create_rectangle(
            30, 31,x, 0, fill=color)

        obj.dist = value
        obj.locLevelTxt = obj.locCanvas.create_text(
            45, 20, fill="black", text=str(obj.dist), font=('Helvetica 16 bold'))

def changeAcc(obj):
    for i in range(0, 80):
        updateAccelerations(obj, [i, i, i])
    for i in range(80, 40, -1):
        updateAccelerations(obj, [i, i, i])
    obj.window.update()
    for i in range(40, 100):
        updateAccelerations(obj, [i, i, i])
    for i in range(100, -1, -1):
        updateAccelerations(obj, [i, i, i])
     
def updateAccelerations(obj, XYZ):
    updateAcceleration(obj.acceleration_X, XYZ[0])
    updateAcceleration(obj.acceleration_Y, XYZ[1])
    updateAcceleration(obj.acceleration_Z, XYZ[2])
    obj.window.update()

def updateAcceleration(obj, value=0):
    if (obj.level > 0) or (obj.level < 100):
        obj.accCanvas.delete(obj.accLevelTxt)
        obj.accCanvas.delete(obj.accLevel)

        x = 120 - int(value*1.04)
        color = colorPicker(value)
        obj.accLevel = obj.accCanvas.create_rectangle(
            0, 120, 31, x, fill=color)  # sol alt,sağ üst

        obj.level = value
        obj.accLevelTxt = obj.accCanvas.create_text(
            16, 110, fill="black", text=str(obj.level), font=('Helvetica 16 bold'))

def changeSpeed(obj):
    for i in range(0, 80):
        updateSpeeds(obj, [i, i, i])
    for i in range(80, 40, -1):
        updateSpeeds(obj, [i, i, i])
    obj.window.update()
    for i in range(40, 100):
        updateSpeeds(obj, [i, i, i])
    for i in range(100, 0, -1):
        updateSpeeds(obj, [i, i, i])

def updateSpeeds(obj,XYZ):
    updateSpeed(obj.speedometer_X, XYZ[0])
    updateSpeed(obj.speedometer_Y, XYZ[1])
    updateSpeed(obj.speedometer_Z, XYZ[2])
    obj.window.update()

def updateSpeed(obj, speed=0):
    if (obj.angle < 270) or (obj.angle > 90):
        obj.angle = 90 + 1.8*speed
        #obj.angle += 1.8
        x = 100 - 100*math.sin(math.radians(obj.angle))
        y = 100 + 100*math.cos(math.radians(obj.angle))
        obj.speedCanvas.delete(obj.speedTxt)
        obj.speedCanvas.delete(obj.speedArrow)
        obj.speedTxt = obj.speedCanvas.create_text(100, 65, fill="black", text=str(
            int((obj.angle-90)/1.8)), font=('Helvetica 20 bold'))
        obj.speedArrow = obj.speedCanvas.create_line(
            100, 100, 0 + x, y, arrow=LAST, width=5, fill="blue")

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

if __name__ == '__main__':
    app = App()
    app.window.bind("<Up>", lambda event, obj=app: {changeLoc(obj),changeAcc(obj),changeSpeed(obj)})
    app.window.protocol('WM_DELETE_WINDOW', lambda obj=app: exit_func(obj))
    app.window.mainloop()
