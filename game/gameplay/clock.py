#Used for animation/transitioning
class Clock:
    def __init__(self):
        self.time = 0

    def tick(self):
        self.time += 1

    def transition(self,frame_duration):
        if self.time >= frame_duration:
            self.time = 0
            return True
        else:
            return False
