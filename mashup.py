from Tkinter import Frame, Canvas, YES, BOTH
import Leap

class TouchPointListener(Leap.Listener):
    def on_init(self, controller):
        self.lefthand = 0 #id
        self.righthand = 0 
        self.leftheight = 0 #y-axis
        self.rightheight = 0
        self.leftsphere = 0 #curvature
        self.rightsphere = 0
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        self.paintCanvas.delete("all")
        frame = controller.frame()
        hands = frame.hands
        left = frame.hand(self.lefthand)
        right = frame.hand(self.righthand)
        if left.is_valid:
            self.leftheight = left.stabilized_palm_position.y
            self.leftsphere = right.sphere_radius
        else:
            self.setHands(hands)

        if right.is_valid:
            self.rightheight = left.stabilized_palm_position.y
            self.rightsphere = right.sphere_radius
        else:
            self.setHands(hands)

        print "Left: %d, Right: %d" % (self.leftheight, self.rightheight)

    def setHands(self, hands):
        if len(hands) == 1:
            self.lefthand = hands[0].id
            self.righthand = hands[0].id
        elif len(hands) > 1:
            l = hands[0]
            r = hands[0]
            for hand in hands:
                if hand.palm_position.x < l.palm_position.x:
                    l = hand
                if hand.palm_position.x > r.palm_position.x:
                    r = hand
            self.lefthand = l.id
            self.righthand = r.id
        else: #no hands on screen
            self.leftheight = 0
            self.rightheight = 0

        '''
        interactionBox = frame.interaction_box
        
        for pointable in frame.pointables:
            normalizedPosition = interactionBox.normalize_point(pointable.tip_position)
            if(pointable.touch_distance > 0 and pointable.touch_zone != Leap.Pointable.ZONE_NONE):
                color = self.rgb_to_hex((0, 255 - 255 * pointable.touch_distance, 0))
                
            elif(pointable.touch_distance <= 0):
                color = self.rgb_to_hex((-255 * pointable.touch_distance, 0, 0))
                #color = self.rgb_to_hex((255,0,0))
                
            else:
                color = self.rgb_to_hex((0,0,200))
                
            self.draw(normalizedPosition.x * 800, 600 - normalizedPosition.y * 600, 40, 40, color)
        '''

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
        self.master.title( "Touch Points" )
        self.master.geometry( "800x600" )
      
        # create Canvas component
        self.paintCanvas = Canvas( self, width = "800", height = "600" )
        self.paintCanvas.pack()
        self.painter.set_canvas(self.paintCanvas)

def main():
    PaintBox().mainloop()

if __name__ == "__main__":
    main()