from Tkinter import *
from Numeric import *

# Version 1.002

class window:
  def __init__(self,width=500,height=500,root_title='Tk plot', plot_title='University of Tokyo, Human Genome Center'):
    self.root = Tk()
    self.root.title(root_title)
    self.canvas = Canvas(self.root,width=width,height=height,background="gray")
    self.canvas.pack()
    self.canvas.create_text(width/2,10,
                            text=plot_title,
                            justify=CENTER)
    self.curves = []
    self.plotitems = []
    self.margin = 30
    self.xmin = None
    self.xmax = None
    self.ymin = None
    self.ymax = None
  def plot(self,y,x=None):
    self.clear()
    n = len(y)
    if x==None: x = arange(n)
    self.curves.append([x,y])
    self.resetaxis(x,y)
    self.redraw()
  def bar(self,y,x,label=[], highlight=0):
    self.clear()
    n = len(y)
    if len(x)==n+1:
      self.ymin = 0
      for i in range(n):
        xl = x[i]
        xr = x[i+1]
        yt = y[i]
        self.curves.append([array([xl,xl,xr,xr]),array([0,yt,yt,0])])
        
      self.resetaxis(x,y,label)
      self.redraw(highlight)
    else:
      return "Error in tkplot, routine bar: parameters are inconsistent"

  def resetaxis(self,x,y,label=[]):
    if self.xmin: self.xmin = min(min(x),self.xmin)
    else: self.xmin = min(x)
    if self.xmax: self.xmax = max(max(x),self.xmax)
    else: self.xmax = max(x)
    if self.ymin: self.ymin = min(min(y),self.ymin)
    else: self.ymin = min(y)
    if self.ymax: self.ymax = max(max(y),self.ymax)
    else: self.ymax = max(y)
    self.xtick =  self.getticks(self.xmax - self.xmin)
    self.ytick =  self.getticks(self.ymax - self.ymin)
    self.xmax = ceil (self.xmax/self.xtick) * self.xtick
    self.xmin = floor(self.xmin/self.xtick) * self.xtick
    self.ymax = ceil(self.ymax/self.ytick) * self.ytick
    self.ymin = floor (self.ymin/self.ytick) * self.ytick
    if label == None:
      self.gettextaxis(label)
    elif len(label) == 0:
      self.getaxis()
    else:
      self.gettextaxis(label)

  def getaxis(self):
    left = self.margin
    right = int(self.canvas['width']) - self.margin
    top = self.margin
    bottom = int(self.canvas['height']) - self.margin
    self.xscale = (right-left)/(self.xmax-self.xmin)
    self.yscale = (top-bottom)/(self.ymax-self.ymin)
    self.plotitems.append (
      self.canvas.create_rectangle(left,bottom,right,top,fill='white'))
    nticks = int(round((self.xmax-self.xmin)/self.xtick))
    width = int(self.canvas['width'])
    height = int(self.canvas['height'])
    y = height - self.margin
    step = (height - 2.*self.margin)/nticks
    for i in range(nticks+1):
      x = self.margin + i * step
      self.plotitems.append(self.canvas.create_line(x,y,x,y-5))
      text = str(self.xmin+i*self.xtick)
      self.plotitems.append(self.canvas.create_text(x,y+10,text=text))
    nticks = int(round((self.ymax-self.ymin)/self.ytick))
    left = self.margin
    right = width - self.margin
    step = (width-2.*self.margin)/nticks
    y = height - self.margin
    for i in range(nticks+1):
      self.plotitems.append(self.canvas.create_line(left,y,left+5,y))
      self.plotitems.append(self.canvas.create_line(right,y,right-5,y))
      text = str(self.ymin+i*self.ytick)
      self.plotitems.append(self.canvas.create_text(left-15,y,text=text))
      y = y - step

  def gettextaxis(self,label):
    left = self.margin
    right = int(self.canvas['width']) - self.margin
    top = self.margin
    bottom = int(self.canvas['height']) - self.margin
    self.xscale = (right-left)/(self.xmax-self.xmin)
    self.yscale = (top-bottom)/(self.ymax-self.ymin)
    self.plotitems.append (
      self.canvas.create_rectangle(left,bottom,right,top,fill='white'))

    nticks = len(label) + 1
    width = int(self.canvas['width'])
    height = int(self.canvas['height'])
    y = height - self.margin
    for i in range(nticks - 1):
      x = self.curves[i][0]
      x = self.margin + self.xscale * (x-self.xmin)
      delta = (x[2] - x[0]) / 2
      x = x[0] + delta
      self.plotitems.append(self.canvas.create_line(x,y,x,y-5))
      text=label[i]
      self.plotitems.append(self.canvas.create_text(x,y+10,text=text))

    nticks = int(round((self.ymax-self.ymin)/self.ytick))
    left = self.margin
    right = width - self.margin
    step = (height-2.*self.margin)/nticks
    y = height - self.margin
    for i in range(nticks+1):
      self.plotitems.append(self.canvas.create_line(left,y,left+5,y))
      self.plotitems.append(self.canvas.create_line(right,y,right-5,y))
      text = str(self.ymin+i*self.ytick)
      self.plotitems.append(self.canvas.create_text(left-15,y,text=text))
      y = y - step

  def getticks(self,length):
    step = length / 5 # five tick marks by default
    goodticks = array([2.0,4.0,5.0,10.0])
    scale = pow(10,floor(log(step)/log(10)))
    index = argmin (abs(step-goodticks*scale))
    besttick = goodticks[index]*scale
    return besttick
  
  def redraw(self, highlight=0):
    left = self.margin
    bottom = int(self.canvas['height']) - self.margin
    for curve in self.curves:
      x = curve[0]
      y = curve[1]
      x = left + self.xscale * (x-self.xmin)
      y = bottom + self.yscale * (y-self.ymin)
      for i in range(len(x)-1):
        item = self.canvas.create_line(x[i],y[i],x[i+1],y[i+1])
        if highlight and i == 1:
          self.canvas.itemconfigure(item,dash=1)
          self.canvas.itemconfigure(item,width=2)
        self.plotitems.append(item)
  def clear(self):
    for item in self.plotitems:
      self.canvas.delete(item)
    self.plotitems = []
    #self.curves = []


