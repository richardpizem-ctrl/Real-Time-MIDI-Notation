"""Piano-roll history preview, in seconds."""
import pygame
class TimelineUI:
    def __init__(self, track_manager, notation_processor=None, width=1240, height=155):
        self.track_manager=track_manager
        self.width=width
        self.height=height
    def draw(self,surface,notes,position,offset=(0,0)):
        rect=pygame.Rect(offset,(self.width,self.height))
        pygame.draw.rect(surface,(24,33,44),rect)
        old=surface.get_clip()
        surface.set_clip(rect)
        left=max(0.0,position-10)
        for second in range(int(left),int(left)+13):
            x=rect.x+int((second-left)*100)
            pygame.draw.line(surface,(45,60,75),(x,rect.y),(x,rect.bottom))
        for note in notes:
            if not self.track_manager.is_effectively_active(note['track_id']):
                continue
            end=position if note['end'] is None else note['end']
            x=rect.x+int((note['timestamp']-left)*100)
            w=max(3,int((end-note['timestamp'])*100))
            y=rect.bottom-int((note['pitch']-35)*self.height/62)
            pygame.draw.rect(surface,self.track_manager.get_color(note['track_id']),(x,y,w,3))
        surface.set_clip(old)
