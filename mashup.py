from Tkinter import *
from tkFileDialog import askopenfilename
import Leap

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

        print "Left: %d, Right: %d" % (self.leftheight, self.rightheight)
        print "LSphere: %d, RSphere: %d" % (self.leftsphere, self.rightsphere)
        
        colorl = self.rgb_to_hex((255-self.leftsphere, self.leftsphere, 0))
        colorr = self.rgb_to_hex((255-self.rightsphere, self.rightsphere, 0))                
        self.draw(250, 600-self.leftheight * 2, self.leftsphere, self.leftsphere, colorl)
        self.draw(550, 600-self.rightheight * 2, self.rightsphere, self.rightsphere, colorr)

    def draw(self, x, y, width, height, color):
        self.paintCanvas.create_oval( x, y, x + width, y + height, fill = color, outline = "")

    def set_canvas(self, canvas):
        self.paintCanvas = canvas
        
    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

class PaintBox(Frame):

    def __init__( self ):
        Frame.__init__( self )
        self.leap = Leap.Controller()
        self.painter = TouchPointListener()
        self.leap.add_listener(self.painter)
        self.pack( expand = YES, fill = BOTH )
        self.master.title( "LeapMashup" )
        self.master.geometry( "1000x800" )

        self.title = Label(self, text = 'Welcome to Leap Mashup!', font = ("Impact", 30))
        self.title.pack()

        # filenames
        self.fileframe = LabelFrame(self, text = "Files")
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

        self.start = Button(self, text = "Begin mashing!", command = self.start)
        self.start.pack()

        # create Canvas component
        self.paintCanvas = Canvas( self, width = "800", height = "600" )
        self.paintCanvas.pack()
        self.painter.set_canvas(self.paintCanvas)

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
        if self.isValidFiles(self.file1path, self.file2path):
            self.painter.STAT = 1
        else:
            raise Exception

    def isValidFiles(self, f1, f2):
        if f1.get()[-4:] != ".wav" or f2.get()[-4:] != ".wav":
            return False
        return True

def main():
    PaintBox().mainloop()

if __name__ == "__main__":
    main()