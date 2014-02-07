
import sys
import struct
import socket
import thread
import time
import Tkinter
import random
import math

def maintain_sensors(soc, sensors):
    while True:
        data = soc.recv(508)
        items = (len(data)/4)-1
        unpacked = struct.unpack("I" + str( items ) + "f", data)

        for i in range(items):
            sensors[unpacked[0] + i] = unpacked[i+1]

def send_request_transmission(soc):
    soc.send(struct.pack("h", 0x2AF6))

def display_histograms(sensors):
    
    # display a logarithmic frequency histogram
    #   Bar 1 is sensors[0:2]
    #       2           [2:4]
    #       3           [4:8] ...
    consider = [x**2 for x in range(2,13)]
    
    while True:
        time.sleep(2)
        print "---------------------------------------------"
        
        for i in consider:
            print sum(sensors[i/2:i])/(i/2)

def save_spectrograms(sensors):
    filename = raw_input("filename base: ")
    reading = 0
    while True:
        f = open(filename + "-" + str(reading+1000) + ".dat", "w")
        for i in range(len(sensors)):
            f.write(str(i) + " " + str(sensors[i]) + "\n")
        f.close()
        reading += 1
        time.sleep(1)

def display_sensors(sensors):
    root = Tkinter.Tk()

    ht = 600
    use_ht = ht-50
    wd = 800

    max_val = math.log(5)

    
    w = Tkinter.Canvas(root, width=wd, height=ht)
    w.pack()

    while True:
        w.delete(Tkinter.ALL)
        time.sleep(.1)
        consider = sensors[10:len(sensors)/12]
        for i in range(len(consider)-1):
            val = math.log(max(1, consider[i]))
            val_n = math.log(max(1, consider[i+1]))
            
            if (val > max_val):
                max_val = val
        
            w.create_line(10 + i*wd/len(consider),
                          (use_ht - val/max_val*use_ht),
                          10 + (i+1)*wd/len(consider),
                          (use_ht - val_n/max_val*use_ht))

        root.update()

def move_sensors(sensors):

    def avg(s):
        sum(s)/len(s)
        
    def add_sensor(ps, curs, num_sens):
        ps.pop(0)
        width = len(curs)/num_sens
        new_sens = [avg([math.log(max(1, s))
                         for s in curs[i*width:(i+1)*width]])
                    for i in range(num_sens)]
                                        
        ps.append(new_sens)
    
    root = Tkinter.Tk()

    ht = 600
    use_ht = ht-50
    wd = 800

    max_val = math.log(5)

    
    w = Tkinter.Canvas(root, width=wd, height=ht)
    w.pack()

    consider_start = 10
    consider_end = len(sensors)/5

    num_hist = 20
    num_sens = 50
    
    past_sensors = [ [0 for j in range(num_sens)]
                     for i in range(num_hist)]

    while True:
        w.delete(Tkinter.ALL)
        time.sleep(.1)
        add_sensor(past_sensors, sensors[consider_start:consider_end],
                   num_sens)
        for i in range(num_hist):        # width
            for j in range(num_sens):    # height
                val = past_sensors[i][j]
                if (val > max_val):
                    max_val = val

                color = hex(int(255-(val/max_val*255)))[2:].upper()
                color_str = "#" + (color*3)

        
                w.create_line(i*wd/num_hist, j,
                              (i+1)*wd/num_hist, j,
                              fill=color_str)
        print "update"
        root.update()
        
if __name__ == '__main__':

    sensors = [0 for i in range(44100)] # never more sensors than this

    
    if len(sys.argv) != 3:
        print "Usage: python client.py <servername> <action>"
        sys.exit()

    host_address = (sys.argv[1], 8843)

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.connect(host_address)
    send_request_transmission(soc)

    thread.start_new_thread(maintain_sensors, (soc, sensors))

    if (sys.argv[2] == "histogram"):
        display_histograms(sensors)
    elif (sys.argv[2] == "spectrogram"):
        save_spectrograms(sensors)
    elif (sys.argv[2] == "display"):
        display_sensors(sensors)
    elif (sys.argv[2] == "move"):
        move_sensors(sensors)
    else:
        print "unknown action.  Allowed actions are:"
        print "  display"
        print "  histogram"
        print "  spectrogram"

            
        
        
