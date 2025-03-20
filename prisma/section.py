import curses
import numpy as np

from dataclasses import dataclass


@dataclass
class _Child:
    sect: Section
    hrel: float
    wrel: float
    yrel: float
    xrel: float


# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, window: curses.window):
        self._win = window
        
        # self.h : int; self.w: int
        # self.y : int; self.x: int
        # self.update_hwyx()
        self.h, self.w = window.getmaxyx()
        self.y, self.x = window.getbegyx()
  
        self._children = {}
        
        self.ystr = 0
        self.xstr = 0
        

    @classmethod
    def newwin(cls, h, w, y, x):
        win = curses.newwin(h, w, y, x)
        return cls(win)

    def addchild(self, name, section, h, w, y, x):
        assert len(name) == 1
        self._children[name] = _Child(section, h, w, y, x)
        return section


    # --------------------------------------------------------------------------
    def mosaic(self, layout: str):
        pass

    # --------------------------------------------------------------------------
    def update_hwyx(self):
        self.h, self.w = window.getmaxyx()
        self.y, self.x = window.getbegyx()

    
    # --------------------------------------------------------------------------
    def erase(self):        
        self.ystr = 0
        self.xstr = 0
              
        self._win.erase()      
        for child in self._children.values():
            child.sect.erase()
        
    def draw(self): 
        self._win.refresh()
        for child in self._children.values():
            child.sect.draw()


    

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        self.h = h
        self.w = w


        self._win.resize(h, w)
        for child in self._children.values():
            hchild = round(child.hrel * h)
            wchild = round(child.wrel * w)
            child.sect.set_size(hchild, wchild)
            
            ychild = round(child.yrel * h)
            xchild = round(child.xrel * w)
            # child.sect.set_pos(ychild, xchild)

                                  

    # --------------------------------------------------------------------------
    # def set_pos(self, y, x):      
    #     for child in self._children.values():            
    #         pass        


        

    # --------------------------------------------------------------------------
    def safe_addstr(self, s, attr = curses.A_NORMAL):
        ### ignore out of bounds error
        try: self._win.addstr(
            self.ystr, self.xstr, s, attr
        )
        except curses.error: pass


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def pystr(self, s, y = None, x = None, attr = curses.A_NORMAL):
        match str(y).upper():
            case None: pass
            case "T"|"TOP":    self.ystr = 0
            case "C"|"CENTER": self.ystr = self.h // 2
            case "B"|"BOTTOM": self.ystr = self.h - 1
            case _:            self.ystr = y

        match str(x).upper():
            case None: pass
            case "L"|"LEFT":   self.xstr = 0
            case "C"|"CENTER": self.xstr = (self.w - len(s)) // 2
            case "R"|"RIGHT":  self.xstr = self.w - len(s)
            case _:            self.xstr = x

        self.safe_addstr(s, attr)

    # -------------------------------------------------------------------------
    def addlayer(self, layer):
        w,h = layer.arr.shape

        mask_f = layer.arr.flatten()
        borders = mask_f.copy()
        borders[1:] ^= mask_f[:-1]
        borders[-1] |= mask_f[-1]
        idxs = np.arange(len(borders))[borders]

        for i0,i1 in zip(idxs[0::2], idxs[1::2]):
            s = (i1-i0)*layer._chars[1] # [TODO] hardcoded
            self.ystr = i0 // h
            self.xstr = i0 % h
            self.safe_addstr(s, layer._attrs[1])

        return layer

    # --------------------------------------------------------------------------

    
    def border(self, *args): self._win.border(*args)


# //////////////////////////////////////////////////////////////////////////////
