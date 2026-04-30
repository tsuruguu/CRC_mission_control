from kivymd.uix.selectioncontrol import MDSwitch

class SpaceSwitch(MDSwitch):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = not self.active
            return True
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            return True
        return False
