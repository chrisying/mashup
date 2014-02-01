from Tkinter import *
from tkFileDialog import askopenfilename
import tkMessageBox
import Leap
import threading
import pygame
import time
import webbrowser

class TouchPointListener(Leap.Listener):
    def on_init(self, controller):
        self.lefthand = 0 #id
        self.righthand = 0 
        self.leftheight = 0 #y-axis
        self.rightheight = 0 #varies from 0ish->200ish
        self.leftsphere = 0 #curvature
        self.rightsphere = 0 #varies from 0ish->200+ish
        self.STAT = 0 #0 = not running, 1 = running
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        if self.STAT == 1:
            self.paintCanvas.delete("all")
            frame = controller.frame()
            hands = frame.hands
            left = frame.hand(self.lefthand)
            right = frame.hand(self.righthand)
            if left.is_valid and ((not left.id == right.id) or len(hands) == 1):
                self.leftheight = left.stabilized_palm_position.y
                self.leftsphere = left.sphere_radius
            else:
                if len(hands) == 1:
                    self.lefthand = hands[0].id
                elif len(hands) > 1:
                    l = hands[0]
                    for hand in hands:
                        if hand.palm_position.x < l.palm_position.x:
                            l = hand
                    self.lefthand = l.id
                else: #no hands on screen
                    self.leftheight = 0
                    self.leftsphere = 0

            if right.is_valid and ((not left.id == right.id) or len(hands) == 1):
                self.rightheight = right.stabilized_palm_position.y
                self.rightsphere = right.sphere_radius
            else:
                if len(hands) == 1:
                    self.righthand = hands[0].id
                elif len(hands) > 1:
                    r = hands[0]
                    for hand in hands:
                        if hand.palm_position.x > r.palm_position.x:
                            r = hand
                    self.righthand = r.id
                else: #no hands on screen
                    self.rightheight = 0
                    self.leftsphere = 0
        
            colorl = self.rgb_to_hex(((255-self.leftsphere) % 256, (2*self.leftsphere) % 256, 0))
            colorr = self.rgb_to_hex(((255-self.rightsphere) % 256, (2*self.rightsphere) % 256, 0))
            self.paintCanvas.create_rectangle(200, 650-self.leftheight, 400, 650, fill = colorl, outline = "")
            self.paintCanvas.create_rectangle(600, 650-self.rightheight, 800, 650, fill = colorr, outline = "")

            print "Left: %d, Right: %d" % (self.leftheight, self.rightheight)
            print "LSphere: %d, RSphere: %d" % (self.leftsphere, self.rightsphere)

    def set_canvas(self, canvas):
        self.paintCanvas = canvas
        
    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

class MusicThread(threading.Thread):
    def __init__(self, sound1, sound2):
        pygame.mixer.init(frequency = 24000)
        threading.Thread.__init__(self)
        self.sound1 = pygame.mixer.Sound(file=sound1)
        self.sound2 = pygame.mixer.Sound(file=sound2)
        self.sound1_volume = 1
        self.sound2_volume = 1
        self.play_command = -1
        self.playing = "Stopped"
        self.listener = None
        self.open = True
    def run(self):
        while self.open:
            if self.listener != None:
                if self.play_command == 0:
                    if self.playing == "Started":
                        pygame.mixer.pause()
                    self.play_command = -1
                    self.playing = "Paused"
                if self.play_command == 1:
                    if self.playing == "Stopped":
                        self.sound1.play()
                        self.sound2.play()
                    if self.playing == "Paused":
                        pygame.mixer.unpause()
                    self.play_command = -1
                    self.playing = "Started"
                if self.playing == "Started":
                    self.sound1_volume = float(self.listener.leftheight - 120) / float(250)
                    self.sound2_volume = float(self.listener.rightheight - 120) / float(250)
                    if self.sound1_volume < 0.0:
                        self.sound1_volume = 0.0
                    if self.sound1_volume > 1.0:
                        self.sound1_volume = 1.0
                    if self.sound2_volume < 0.0:
                        self.sound2_volume = 0.0
                    if self.sound2_volume > 1.0:
                        self.sound2_volume = 1.0
                    self.sound1.set_volume(self.sound1_volume)
                    self.sound2.set_volume(self.sound2_volume)
            time.sleep(0.02)
        self.playing = "Stopped"
        pygame.mixer.stop()

class PaintBox(Frame):
    def __init__( self ):
        Frame.__init__(self, background = "#080808")
        self.leap = Leap.Controller()
        self.painter = TouchPointListener()
        self.leap.add_listener(self.painter)
        self.pack( expand = YES, fill = BOTH )
        self.master.title( "LeapMashup" )
        self.master.geometry( "1000x800" )
        self.bgcol = "#040404"

        self.log = PhotoImage(file = "logo.gif")
        self.logo = Canvas(self, width = 800, height = 100, background = "#080808", highlightthickness = 0)
        self.logo.pack()
        self.logo.create_image(0, 0, image = self.log, anchor = NW)
        self.title = Label(self, text = 'a Leap Mashup app', font = ("Helvetica", 20), background = self.bgcol, foreground = "#ffffff")
        self.title.pack()

        # filenames
        self.fileframe = LabelFrame(self, text = "Files", background = self.bgcol, foreground = "#ffffff", relief = SUNKEN)
        self.fileframe.pack()

        self.f1 = LabelFrame(self.fileframe)
        self.f1.pack(side = "left")
        self.file1path = StringVar()
        self.file1path.set("First file")
        self.file1 = Label(self.f1, textvariable = self.file1path, width = 30, relief = SUNKEN)
        self.file1.pack(side = "left")
        self.button1 = Button(self.f1, text = "Select", command = self.getFile1)
        self.button1.pack(side = "right")

        self.f2 = LabelFrame(self.fileframe)
        self.f2.pack(side = "right")
        self.file2path = StringVar()
        self.file2path.set("Second file")
        self.file2 = Label(self.f2, textvariable = self.file2path, width = 30, relief = SUNKEN)
        self.file2.pack(side = "left")
        self.button2 = Button(self.f2, text = "Select", command = self.getFile2)
        self.button2.pack(side = "right")

        self.tpanel = LabelFrame(self)
        self.tpanel.pack(side = "top")
        self.start = Button(self.tpanel, text = "Begin mashing!", command = self.start)
        self.start.pack(side = "left")
        self.pause = Button(self.tpanel, text = "Pause mashing!", command = self.pause)
        self.pause.pack(side = "left")
        self.stop = Button(self.tpanel, text = "Stop mashing!", command = self.stop)
        self.stop.pack(side = "left")
        self.exit = Button(self.tpanel, text = "Exit mashing!", command = self.ask_exit)
        self.exit.pack(side = "left")

        self.bpanel = LabelFrame(self)
        self.bpanel.pack(side = "bottom")
        self.save = Button(self.bpanel, text = "Save mashing!")
        self.save.pack(side = "left")
        self.upload = Button(self.bpanel, text = "Upload mashing!")
        self.upload.pack(side = "left")
        self.share = Button(self.bpanel, text = "Share mashing!")
        self.share.pack(side = "left")
        self.skynet = Button(self.bpanel, text = "Activate Skynet", command = self.sky)
        self.skynet.pack(side = "left")

        # create Canvas component
        self.paintCanvas = Canvas(self, width = "1000", height = "650", bd = 0, background = self.bgcol, highlightthickness = 0)
        self.paintCanvas.pack()
        self.painter.set_canvas(self.paintCanvas)

        self.music = None

    def getFile1(self):
        f = self.getFile()
        if f == "":
            f = "No file"
        elif f[-4:] != ".wav":

            f = "Invalid format"
        self.file1path.set(f)

    def getFile2(self):
        f = self.getFile()
        if f == "":
            f = "No file"
        elif f[-4:] != ".wav":
            f = "Invalid format"
        self.file2path.set(f)

    def getFile(self):
        f = askopenfilename()
        return f

    def start(self):
        if self.music == None:
            if self.isValidFiles(self.file1path, self.file2path):
                self.painter.STAT = 1
                self.music = MusicThread(self.file1path.get(), self.file2path.get())
                self.music.play_command = 1
                self.music.listener = self.painter
                self.music.start()
            else:
                raise Exception
        else:
            self.painter.STAT = 1
            self.music.play_command = 1

    def pause(self):
        if self.music != None:
            self.painter.STAT = 0
            self.music.play_command = 0

    def stop(self):
        if self.music != None:
            self.painter.STAT = 0
            self.music.open = False
            self.music = None
    
    def ask_exit(self):
        if tkMessageBox.askokcancel("Exit", "Exit playing?"):
            self.master.destroy()
            self.painter.STAT = 0
            if self.music != None:
                self.music.open = False
                self.music = None

    def isValidFiles(self, f1, f2):
        if f1.get()[-4:] != ".wav" or f2.get()[-4:] != ".wav":
            return False
        return True

    def sky(self):
        webbrowser.open("http://youtu.be/_Wlsd9mljiU?t=2m51s")

def main():
    PaintBox().mainloop()

if __name__ == "__main__":
    main()
