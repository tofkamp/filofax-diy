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
class pdfout():
  """
  Create xfig files with coordinates in millimeters

  @ivar orientation: Orientation of the paper ("Landscape" or "Portrait")
  @type orientation: C{str}

  @ivar paperheight: Height of the paper
  @type paperheight: C{float}

  @ivar magnification: export and print magnification, %
  @type magnification: C{float}

  @ivar resolution: Fig units/inch and coordinate system
  @type resolution: C{int}

  @ivar drawing: Buffer for holding the drawing on the paper
  @type drawing: C{str}

  @ivar xorigin: X-offset to draw functions
  @type xorigin: C{int}

  @ivar yorigin: Y-offset to draw functions
  @type yorigin: C{int}

  @ivar originstack: The stack holding the origins
  @type originstack: C{[(int, int)]}

  """

  #  ['Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique', 'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique', 'Symbol', 'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman', 'ZapfDingbats']

  def __init__(self,width,height):
    #self.paperwidth = width
    self.paperheight = height
    self.resolution = 72	        #Fig units/inch and coordinate system:
    self.drawings = []

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
  
  def line(self,fx,fy,dx,dy,style=0,dikte=1,gray=0):
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
    self.drawings.append(('L',self.mm2pos(self.xorigin+fx),self.mm2pos(self.paperheight-(self.yorigin+fy)),
                          self.mm2pos(self.xorigin+fx+dx),self.mm2pos(self.paperheight-(self.yorigin+fy+dy)),
                          style,dikte,gray))
    # add gray color default to 0
    # for gray in (0.0, 0.25, 0.50, 0.75, 1.0):        canvas.setFillGray(gray)
     
  def tekst(self,x,y,text,font='Helvetica',fsize=12,align=0,gray=0):
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

    @param fsize: The size of the font in 1/72"
    @type  fsize: C{int}

    @param align: Align the tekst left(0),centre(1) or right(2)
    @type  align: C{int}
    """
    self.drawings.append(('T',self.mm2pos(self.xorigin+x), self.mm2pos(self.paperheight-(self.yorigin+y)), text,font,fsize,align,gray))

  def circle(self,x,y,rad,style=0,dikte=1,gray=0):
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

    @param dikte: Thickness of the circle in 1/72"
    @type  dikte: C{int}
    """
    self.drawings.append(('C',self.mm2pos(self.xorigin+x), self.mm2pos(self.paperheight-(self.yorigin+y)),self.mm2pos(rad),style,dikte,gray))

  def mm2pos(self,mm):
    """
    Calculate mm to xfig units
    self.resolution is expressed in units/xfig-inch.

    @param mm: distance in mm
    @type  mm: C{float}

    @return: The number of fig units for the given distance
    @rtype:  C{int}
    """
    return mm*self.resolution/25.4

  def save(self,pdf):
    """
    Write the drawing to a file

    @param filename: The complete filename to which the drawing has to be written
    @type  filename: C{str}
    """
    for cmd in self.drawings:
      if cmd[0] == 'L':
        # line x,y,x2,y2,style,dikte,gray=0
        pdf.setLineWidth(cmd[6])
        pdf.setStrokeGray(cmd[7])
        if cmd[5] == 0:   # solid
          pdf.setDash()
        else:    # 2 == dashed
          pdf.setDash(1,2)
          #canvas.setDash(self, array=[], phase=0) 
        pdf.line(cmd[1],cmd[2],cmd[3],cmd[4])
      elif cmd[0] == 'C':   # circle(self,x,y,rad,style=0,dikte=1,gray=0):
        pdf.setLineWidth(cmd[5])
        pdf.setStrokeGray(cmd[6])
        if cmd[4] == 0:   # solid
          pdf.setDash()
        else:    # 2 == dashed
          pdf.setDash(1,2)
        pdf.circle(cmd[1],cmd[2],cmd[3])
      elif cmd[0] == 'T':   # tekst(self,x,y,text,font=0,fsize=12,align=0,gray=0):
        #print(cmd[4],cmd[5])
        pdf.setFont(cmd[4],cmd[5])
        pdf.setStrokeGray(cmd[7])
        if cmd[6] == 0:    # left align
          pdf.drawString(cmd[1],cmd[2], cmd[3])
        elif cmd[6] == 1:   # centre
          pdf.drawCentredString(cmd[1],cmd[2], cmd[3])
        else: #cmd[6] == 2:
          pdf.drawRightString( cmd[1],cmd[2], cmd[3])
      else:
        error("unknown command")
    self.drawings=[]
    pdf.showPage()
