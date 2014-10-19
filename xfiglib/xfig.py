""" Copyright (C) 2014 T.Hofkamp

    This file is part of FilofaxDIY.

    FilofaxDIY is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    FilofaxDIY is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with FilofaxDIY.  If not, see <http://www.gnu.org/licenses/>.

"""
class xfig():
  """
  Create xfig files with coordinates in millimeters

  @ivar orientation: Orientation of the paper ("Landscape" or "Portrait")
  @type orientation: C{str}

  @ivar justification: ("Center" or "Flush Left")
  @type justification:

  @ivar units: "Metric" or "Inches"
  @type units: C{str}

  @ivar papersize: "Letter", "Legal", "Ledger", "Tabloid",
		   "A", "B", "C", "D", "E",
		   "A4", "A3", "A2", "A1", "A0" and "B5"
  @type papersize: C{str}

  @ivar magnification: export and print magnification, %
  @type magnification: C{float}

  @ivar multiplepage: Printing on single or multiple pages ("Single" or "Multiple")
  @type multiplepage: C{str}

  @ivar transparentcolor: color number for transparent color for GIF
			  export. -3=background, -2=None, -1=Default,
			  0-31 for standard colors or 32- for user colors)
  @type transparentcolor: C{int}

  @ivar resolution: Fig units/inch and coordinate system
  @type resolution: C{int}

  @ivar coord_system: The place of origin 1=lower left (NOT USED), 2=upper left
  @type coord_system: C{int}

  @ivar drawing: Buffer for holding the drawing on the paper
  @type drawing: C{str}

  @ivar depth: Layer on which to draw
  @type depth: C{int}

  @ivar xorigin: X-offset to draw functions
  @type xorigin: C{int}

  @ivar yorigin: Y-offset to draw functions
  @type yorigin: C{int}

  @ivar originstack: The stack holding the origins
  @type originstack: C{[(int, int)]}

  """
  """
  -1	Default font
	 0	Times Roman
	 1	Times Italic
	 2	Times Bold
	 3	Times Bold Italic
	 4	AvantGarde Book
	 5	AvantGarde Book Oblique
	 6	AvantGarde Demi
	 7	AvantGarde Demi Oblique
	 8	Bookman Light
	 9	Bookman Light Italic
	10	Bookman Demi
	11	Bookman Demi Italic
	12	Courier
	13	Courier Oblique
	14	Courier Bold
	15	Courier Bold Oblique
	16	Helvetica
	17	Helvetica Oblique
	18	Helvetica Bold
	19	Helvetica Bold Oblique
	20	Helvetica Narrow
	21	Helvetica Narrow Oblique
	22	Helvetica Narrow Bold
	23	Helvetica Narrow Bold Oblique
	24	New Century Schoolbook Roman
	25	New Century Schoolbook Italic
	26	New Century Schoolbook Bold
	27	New Century Schoolbook Bold Italic
	28	Palatino Roman
	29	Palatino Italic
	30	Palatino Bold
	31	Palatino Bold Italic
	32	Symbol
	33	Zapf Chancery Medium Italic
	34	Zapf Dingbats
  """
  
  def __init__(self,paper = "Letter", orient = "Portrait"):
    self.orientation = orient   	#"Landscape" or "Portrait"
    self.justification	= "Center"	#"Center" or "Flush Left"
    self.units	= "Metric"		#"Metric" or "Inches"
    self.papersize = paper		#"Letter", "Legal", "Ledger", "Tabloid",
					# "A", "B", "C", "D", "E",
					# "A4",   "A3", "A2", "A1", "A0" and "B5"
    self.magnification = 100.0	        #export and print magnification, %
    self.multiplepage = "Single"        #"Single" or "Multiple" pages
    self.transparentcolor = -2	        #color number for transparent color for GIF
					# export. -3=background, -2=None, -1=Default,
					# 0-31 for standard colors or 32- for user colors)
					# which are associated with the whole figure)
    self.resolution = 1200	        #Fig units/inch and coordinate system:
    self.coord_system=2 		#  1: origin at lower left corner (NOT USED)
					#   2: upper left)
    self.drawing = ""

    self.depth = 50                     # the depth/layer to draw on

    self.xorigin = 0
    self.yorigin = 0
    self.originstack = []
  def pushorigin(self,dx,dy):
    """
    Push the current origin to the stack, and move it relative to (dx,dy)

    @param dx: Delta x to move the origin to
    @type  dx: C{int}

    @param dy: Delta y to move the origin to
    @type  dy: C{int}
    """
    self.originstack.append((self.xorigin,self.yorigin))
    self.xorigin += dx
    self.yorigin += dy
    
  def poporigin(self):
    """
    Return to the previous origin
    """
    (self.xorigin,self.yorigin) = self.originstack.pop()
    
  def setorigin(self,x,y):
    """
    Set the current origin, clearing the stack

    @param x: x to move the origin to
    @type  x: C{int}

    @param y: y to move the origin to
    @type  y: C{int}
    """
    self.originstack = []
    self.xorigin = x
    self.yorigin = y
    
  def setdepth(self,newdepth):
    """
    Set the layer to draw to

    @param newdepth: The layer number (0...999)
    @type  newdepth: C{int}
    """
    self.depth = newdepth

  def getpaperwidth(self):
    """
    Return the width of the paper

    @return: The width in mm
    @rtype:  C{int}
    """
    paper={
    "4A0":( 1682 , 2378),
    "2A0":( 1189 , 1682),
    "A0":( 841 , 1189),
    "A1":( 594 , 841),
    "A2":( 420 , 594),
    "A3":( 297 , 420),
    "A4":(210,297),
    "A5":( 148 , 210),
    "A6":( 105 , 148),
    "A7":(74 , 105),
    "A8":( 52 , 74),
    "A9":( 37 , 52),
    "A10":( 26 , 37),
    "Letter":( 216 , 279),
    "Legal":( 216 , 356),
    "Junior Legal":( 127 , 203),
    "Ledger/Tabloid":( 279 , 432), 
    "A":( 216 , 279),
    "B":( 279 , 432),
    "C":( 432 , 559),
    "D":( 559 , 864),
    "E":( 864 , 1118) }
    if self.orientation == "Portrait":
      return paper[self.papersize][0]
    return paper[self.papersize][1]
  

  def getpaperheight(self):
    """
    Return the height of the paper

    @return: The height in mm
    @rtype:  C{int}
    """
    # should be based on some kind of table, and orientation
    paper={
    "4A0":( 1682 , 2378),
    "2A0":( 1189 , 1682),
    "A0":( 841 , 1189),
    "A1":( 594 , 841),
    "A2":( 420 , 594),
    "A3":( 297 , 420),
    "A4":(210,297),
    "A5":( 148 , 210),
    "A6":( 105 , 148),
    "A7":(74 , 105),
    "A8":( 52 , 74),
    "A9":( 37 , 52),
    "A10":( 26 , 37),
    "Letter":( 216 , 279),
    "Legal":( 216 , 356),
    "Junior Legal":( 127 , 203),
    "Ledger/Tabloid":( 279 , 432), 
    "A":( 216 , 279),
    "B":( 279 , 432),
    "C":( 432 , 559),
    "D":( 559 , 864),
    "E":( 864 , 1118) }
    if self.orientation == "Portrait":
      return paper[self.papersize][1]
    return paper[self.papersize][0]
  
  def line(self,fx,fy,dx,dy,style=0,dikte=1):
    """
    Draw a line from (fx,fy) to (fx+dx,fy+dy) with the style an thickness (1/80")
    Coordinates are relative to self.origin

    @param fx: fx From this X point
    @type  fx: C{int}

    @param fy: fy From this Y point
    @type  fy: C{int}

    @param dx: dx Draw relative to X point
    @type  dx: C{int}

    @param dy: dy Draw relative to Y point
    @type  dy: C{int}

    @param style: The style of the line 0=SOLID
    @type  style: C{int}

    @param dikte: Thickness of the line in 1/80"
    @type  dikte: C{int}
    """
    self.writeline("2 1 "+str(style)+" "+str(dikte)+" 0 7 "+str(self.depth)+" -1 -1 0.000 0 0 -1 0 0 2")
    self.writeline("\t"+str(self.mm2pos(self.xorigin+fx))+" "+str(self.mm2pos(self.yorigin+fy))+" "+str(self.mm2pos(self.xorigin+fx+dx))+" "+str(self.mm2pos(self.yorigin+fy+dy)))
    
  def tekst(self,x,y,text,font=0,fsize=12,align=0):
    """
    Write some tekst to the canvas
    Coordinates are relative to origin
    
    @param x: X point to start (depending on align)
    @type  x: C{int}

    @param y: Y of lower point of tekst
    @type  y: C{int}

    @param text: The actual text to show
    @type  text: C{str}

    @param font: Font number to draw (LaTeX ??)
    @type  font: C{int}

    @param fsize: The size of the font in 1/80"
    @type  fsize: C{int}

    @param align: Align the tekst left(0),centre(1) or right(2)
    @type  align: C{int}
    """
    #self.writeline("4 "+str(align)+" 0 "+str(self.depth)+" -1 "+str(font)+" "+str(fsize)+" 0.0000 6 135 480 "+str(self.mm2pos(x))+" "+str(self.mm2pos(y))+" "+text+"\\001")
    line = "4 {align} 0 {depth} -1 {font} {fsize} 0.0000 6 135 480 {x} {y} {text}\\001"
    line = line.format(align = align, depth = self.depth, font = font, fsize = fsize,
      x = self.mm2pos(self.xorigin+x), y = self.mm2pos(self.yorigin+y), text = text)
    self.writeline(line)

  def circle(self,x,y,rad,style=0,dikte=1):
    """
    Draw a circle on centre (x,y) with the given radius, relative to origin

    @param x: x Centre of circle
    @type  x: C{int}

    @param y: y Centre of circle
    @type  y: C{int}

    @param rad: Radius circle
    @type  rad: C{int}

    @param style: The style of the circle 0=SOLID
    @type  style: C{int}

    @param dikte: Thickness of the circle in 1/80"
    @type  dikte: C{int}
    """
    # also something with fillig, future
    self.ellipse(x,y,rad,rad,style,dikte)   # ellipse is also a circle
#    self.writeline("1 3 "+str(style)+" "+str(dikte)+" 0 7 "+str(self.depth)+" -1 -1 0.000 1 0.0000 "+str(self.mm2pos(x))+" "+str(self.mm2pos(y))+" "+str(self.mm2pos(rad))+" "+str(self.mm2pos(rad))+" "+str(self.mm2pos(x))+" "+str(self.mm2pos(y))+" "+str(self.mm2pos(x+rad))+" "+str(self.mm2pos(y)))
    #line = "1 3 {style} {dikte} 0 7 {depth} -1 -1 0.000 1 0.0000 {x} {y} {radius} {radius} {x} {y} {xi} {y}"
    #line = line.format(style = style, dikte = dikte, depth = self.depth, x = self.mm2pos(self.xorigin+x), y = self.mm2pos(self.yorigin+y),
    #                   radius = self.mm2pos(rad), xi = self.mm2pos(self.xorigin+x+rad))
    #self.writeline(line)                   

  def ellipse(self,x,y,xrad,yrad,style=0,dikte=1):
    """
    Draw a circle on centre (x,y) with the given radius, relative to origin

    @param x: x Centre of circle
    @type  x: C{int}

    @param y: y Centre of circle
    @type  y: C{int}

    @param xrad: Radius circle horizontal
    @type  xrad: C{int}

    @param yrad: Radius circle vertical
    @type  yrad: C{int}

    @param style: The style of the circle 0=SOLID
    @type  style: C{int}

    @param dikte: Thickness of the circle in 1/80"
    @type  dikte: C{int}
    """
    line = "1 3 {style} {dikte} 0 7 {depth} -1 -1 0.000 1 0.0000 {x} {y} {radiusx} {radiusy} {x} {y} {xi} {y}"
    line = line.format(style = style, dikte = dikte, depth = self.depth, x = self.mm2pos(self.xorigin+x), y = self.mm2pos(self.yorigin+y),
                       radiusx = self.mm2pos(xrad), radiusy = self.mm2pos(yrad), xi = self.mm2pos(self.xorigin+x+xrad))
    self.writeline(line)                   

  def box(self,fx,fy,w,h,style=0,dikte=1):
    """
    Draw a box from (fx,fy) to (fx+w,fy+h) with the style an thickness (1/80")
    Coordinates are relative to self.origin

    @param fx: From this X point
    @type  fx: C{int}

    @param fy: From this Y point
    @type  fy: C{int}

    @param w: The width of the box
    @type  w: C{int}

    @param h: h The height of the box
    @type  h: C{int}

    @param style: The style of the line 0=SOLID
    @type  style: C{int}

    @param dikte: Thickness of the line in 1/80"
    @type  dikte: C{int}
    """
    self.writeline("2 2 "+str(style)+" "+str(dikte)+" 0 7 "+str(self.depth)+" -1 -1 0.000 0 0 -1 0 0 5")
    line = "\t{x1} {y1} {x2} {y1} {x2} {y2} {x1} {y2} {x1} {y1}"
    line = line.format(x1 = self.mm2pos(self.xorigin+fx), y1 = self.mm2pos(self.yorigin+fy),
                       x2 = self.mm2pos(self.xorigin+fx+w), y2 = self.mm2pos(self.yorigin+fy+h))
    self.writeline(line)

  def mm2pos(self,mm):
    """
    Calculate mm to xfig units
    self.resolution is expressed in units/xfig-inch. This xfig-inch is 2.667 cm (1.050") on paper

    @param mm: distance in mm
    @type  mm: C{float}

    @return: The number of fig units for the given distance
    @rtype:  C{int}
    """
    figunitspermm=140*self.resolution/6300.0
    return int(round(mm*self.resolution/figunitspermm))
    #	return int(round(mm*resolution/25.4))

  def comment(self,comment):
    """
    Add some comment in the file

    @param comment: The line of comment
    @type  comment: C{str}
    """
    self.drawing += '#' + comment + "\n"
    
  def writeline(self,line):
    """
    Add a line of output to the drawing

    @param line: The line of output for xfig
    @type  line: C{str}
    """
    self.drawing += line + "\n"

  def save(self,filename):
    """
    Write the drawing to a file

    @param filename: The complete filename to which the drawing has to be written
    @type  filename: C{str}
    """
    # write out some header
    f = open(filename,mode='w')
    f.write('#FIG 3.2\n')
    f.write('# Created by FiloFax version 1.0\n')
    f.write(self.orientation + '\n')
    f.write(self.justification + '\n')
    f.write(self.units + '\n')
    f.write(self.papersize + '\n')
    f.write(str(self.magnification) + '\n')
    f.write(self.multiplepage + '\n')
    f.write(str(self.transparentcolor) + '\n')
    f.write(str(self.resolution) + ' ' + str(self.coord_system) + '\n')
    f.write(self.drawing)
    f.close()
