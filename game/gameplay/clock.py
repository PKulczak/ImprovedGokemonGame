#Used for animation/transitioning
class Clock:
    def __init__(self):
        self.time = 0

    #dt is in frame-equivalents (1.0 == one frame at the nominal 60fps design rate) - see
    #frame.py's main loop, which is the only place that derives it from real elapsed time
    def tick(self, dt):
        self.time += dt

    def transition(self,frame_duration):
        if self.time >= frame_duration:
            self.time = 0
            return True
        else:
            return False
