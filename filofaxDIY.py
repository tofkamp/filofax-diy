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
import locale
import datetime
from xfiglib import pdfout    # name is not logical
import argparse
from reportlab.pdfgen import canvas
import reportlab.lib.pagesizes
from reportlab.lib.units import cm

FILOFAXDIYVERSION="https://code.google.com/p/filofax-diy/"    # should be from versioning system, but how can I do this ????

class filofax:
  def __init__(self,language,font,lineheight,paper,orient,filename,filofax):
    if language != None:
      locale.setlocale(locale.LC_TIME,language)
    #statics
    self.font= font    # which font to use
    self.headerfont=self.font    # header font will be the same
    self.headerfsize=10  # fontsize in 1/72" for header on top of page
    self.headerheight=11  # height in mm for header on top of page
    self.mdayfont=self.font  # monthday font  (1..31)
    self.mdayfsize=19
    self.dayofweekfont=self.font   # name of the weekday font (eg monday)
    self.dayofweekfsize=9

    #self.agendawidth=95.0
    #self.agendaheight=171.0
    self.agendawidth=filofax[0]    # how large is one agenda page
    self.agendaheight=filofax[1]
    self.nrholes = filofax[2]     # nr of holes / 2, rounded up
    self.holesoffset = filofax[3]  # offset from middle
    self.holesstep = filofax[4]   # space between holes
    self.lineheight = lineheight  # space between lines in one agenda day
    # create the reportlab pdf stream
    self.canvas = canvas.Canvas(filename,pageCompression=1,verbosity=0)    #,pagesize=A4,bottumup = 0,pageCompression=0,
    if orient == 'Portrait':
      self.canvas.setPageSize(reportlab.lib.pagesizes.portrait(paper))
    else:
      self.canvas.setPageSize(reportlab.lib.pagesizes.landscape(paper))
    self.canvas.setAuthor('T.Hofkamp')
    self.canvas.setCreator(FILOFAXDIYVERSION)
    self.canvas.setTitle('Agenda')
    self.canvas.setSubject('FilofaxDIY printable agenda')
     
    """
    personal  95x171    holes 5.5mm at 5mm from edge at 26,45,64mm from midle
    A5        148x210
    pocket    81x120
    a4        210x297
    mini      67x105
    """

    self.cutlinelength = 10   # the length of the cutlines between the agenda pages
    self.outermargin = 5    # margin at the edge
    self.innermargin = 10   # margin at the holes

    """ is now filled with the program, depending on the size of the paper
    Try to fit as many agenda-pages as you can, on one paper page.
    # the next 5 vars can be derived from papersize and agendapagesize
    self.agendapagesperpage = 3     # xcount =3,ycount=1  count=xcount*ycount
    self.evenpageorigins = [(6.0, 19.5), (101.0, 19.5), (196.0, 19.5)]
    self.oddpageorigins = [(196.0, 19.5), (101.0, 19.5), (6.0, 19.5)]
    self.cutlinesx = (6,101,196,291)
    self.cutlinesy = (19.5,190.5)
    """
    
    self.paperwidth = self.canvas._pagesize[0] * 10 / cm          # calculate the width in mm from the choosen paper parameter
    self.paperheight = self.canvas._pagesize[1] * 10 / cm         # calculate the height in mm from the choosen paper parameter
    xcount = int(self.paperwidth / self.agendawidth)
    ycount = int(self.paperheight / self.agendaheight)
    self.agendapagesperpage = xcount * ycount
    # assert(self.agendapagesperpage > 0)
    startx = (self.paperwidth - xcount * self.agendawidth) / 2.0    # where does the first agendapage start
    starty = (self.paperheight - ycount * self.agendaheight) / 2.0
    self.cutlinesx = []
    for x in range(xcount + 1):
      self.cutlinesx.append(startx + x * self.agendawidth)
    self.cutlinesy = []
    for y in range(ycount + 1):
      self.cutlinesy.append(starty + y * self.agendaheight)
    self.evenpageorigins = []     # the origins of the agenda pages on the page (mm) left to right, and down
    self.oddpageorigins = []      # almost equal to the evenpageorigins, only from right to left, and then down
    for y in range(ycount):
      for x in range(xcount):
        self.evenpageorigins.append((self.cutlinesx[x],self.cutlinesy[y]))
      for x in range(xcount-1,-1,-1):
        self.oddpageorigins.append((self.cutlinesx[x],self.cutlinesy[y]))
    
    #dynamic vars
    self.currentonevenpage = False    # true or false,depending on which side of paper
    self.currentagendapage = self.agendapagesperpage - 1   # point to last agenda page
    # because reportlab pdf, cannot write to two pages at the same time, all draw actions are bufferd
    # with pdfout object, evenpage and oddpage contains the buffered draw action
    self.evenpage = None     # the buffers
    self.oddpage = None
    self.currentpage = self.oddpage   # point to the current object for buffering
    
  def titlepage(self,year):
    """
    Make the title page

    Maybe add GLPv3 logo in the future
    @param year: The year for which the agenda is created
    @type  year: C(int)
    """
    self.formfeed()    # start on a new agenda page
    self.assertevenpage()
    # Show the year at 1/3 of page
    self.currentpage.tekst(self.outermargin+(self.agendawidth-self.innermargin-self.outermargin)/2,self.agendaheight/3,year,self.font,48,1)
    # show the program name and version at 7/8 of the page
    self.currentpage.tekst(self.outermargin+(self.agendawidth-self.innermargin-self.outermargin)/2,self.agendaheight*7/8,FILOFAXDIYVERSION,self.font,8,1)
    self.currentpage.image('gplv3.jpg',self.innermargin+5,self.agendaheight-10,7.38,3.77)
    
  def calender(self,year):
    pass

  def monthplanner(self):
    pass

  def drawday(self,day,height,width):
    """
    Draw just one day, Linespacing is determined by self.lineheight, except when it is 0, no lines are drawn
    On the bottom a thick line is draw as seperation to the next day or end of agenda paper
    
    @param day: The day for which to draw the agenda
    @type  day: C(datetime.date)

    @param height: The height to draw the day in (mm)
    @param height: C(float)

    @param width: The height to draw the day in (mm)
    @param width: C(float)
    """
    leftindent = 0
    rightindent = 0
    if self.currentonevenpage:
      # evenpage,when holes are on left
      self.currentpage.tekst(width,5,str(int(day.strftime("%d"))),self.mdayfont,self.mdayfsize,2)  #day of the month
      self.currentpage.tekst(width - 10,3,day.strftime("%A"),self.dayofweekfont,self.dayofweekfsize,2)  # day of the week
      self.currentpage.tekst(0,3,day.strftime("%j"),self.dayofweekfont,self.dayofweekfsize,0)
      rightindent = 10
    else:
      # oddpage,when holes are on right
      self.currentpage.tekst(0,5,str(int(day.strftime("%d"))),self.mdayfont,self.mdayfsize,0)
      self.currentpage.tekst(10,3,day.strftime("%A"),self.dayofweekfont,self.dayofweekfsize,0)
      self.currentpage.tekst(width,3,day.strftime("%j"),self.dayofweekfont,self.dayofweekfsize,2)
      leftindent = 10
    if self.lineheight > 0:
      i = 6
      while i + self.lineheight < height - 2:
        self.currentpage.line(leftindent,i,width-leftindent-rightindent,0,2,0.5)
        i = i + self.lineheight
        if i > 10:
          leftindent = 0
          rightindent = 0
    self.currentpage.line(0,height - 2,width,0,0,2)
  
  def weekon2pages(self,day):
    """
    @param day: C(datetime.date)
    
    Draw the week from "day", to the agenda pages. 3 times a workday, and 2 workdays, and 2 weekend days
    In the future, check the height for using it with other formats
    Collect month names in order to fill header
    """
    wdayheight = 52.0
    wendheight = wdayheight / 2
    width = self.agendawidth - self.innermargin - self.outermargin
    self.formfeed()
    self.assertoddpage()

    self.currentpage.pushorigin(self.outermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(0,7,day.strftime("%Y"),self.headerfont,self.headerfsize,0)    #year
    self.currentpage.tekst(10,7,day.strftime("%B"),self.headerfont,self.headerfsize,0)     # month
    self.currentpage.tekst(width,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,2)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # monday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wdayheight)
    # tuesday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wdayheight)
    # wednesday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.poporigin()
    self.currentpage.poporigin()
    self.currentpage.poporigin()
    self.currentpage.poporigin()
    self.formfeed()

    self.currentpage.pushorigin(self.innermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(width,7,day.strftime("%Y"),self.headerfont,self.headerfsize,2)    #year
    self.currentpage.tekst(width - 10,7,day.strftime("%B"),self.headerfont,self.headerfsize,2)     # month
    self.currentpage.tekst(0,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,0)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # thursday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wdayheight)
    # friday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wdayheight)
    # saturday
    self.drawday(day,wendheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wendheight)
    # sunday
    self.drawday(day,wendheight,width)
    #day += datetime.date.resolution
    self.currentpage.poporigin()
    self.currentpage.poporigin()
    self.currentpage.poporigin()
    self.currentpage.poporigin()
    self.currentpage.poporigin()
    # header doen
    
  def weekon6pages(self,day):
    """
    @param day: C(datetime.date)
    
    Draw the week from "day", to the agenda pages. 5 times a workday, and 1x 2 days for the weekend
    In the future, check the height for using it with other formats
    It would be better to use more functions, eg header()
    """
    # assert(dayofweek(day) == monday)
    # future collect month names in order to fill header
    wdayheight = 52.0 * 3
    wendheight = wdayheight / 2
    width = self.agendawidth - self.innermargin - self.outermargin
    self.formfeed()
    self.assertoddpage()

    self.currentpage.pushorigin(self.outermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(0,7,day.strftime("%Y"),self.headerfont,self.headerfsize,0)    #year
    self.currentpage.tekst(10,7,day.strftime("%B"),self.headerfont,self.headerfsize,0)     # month
    self.currentpage.tekst(width,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,2)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # monday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.poporigin()
    self.formfeed()

    self.currentpage.pushorigin(self.innermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(width,7,day.strftime("%Y"),self.headerfont,self.headerfsize,2)    #year
    self.currentpage.tekst(width - 10,7,day.strftime("%B"),self.headerfont,self.headerfsize,2)     # month
    self.currentpage.tekst(0,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,0)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # tuesday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wdayheight)
    self.currentpage.poporigin()

    self.formfeed()
    self.currentpage.pushorigin(self.outermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(0,7,day.strftime("%Y"),self.headerfont,self.headerfsize,0)    #year
    self.currentpage.tekst(10,7,day.strftime("%B"),self.headerfont,self.headerfsize,0)     # month
    self.currentpage.tekst(width,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,2)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # wednesday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.poporigin()
    self.formfeed()

    self.currentpage.pushorigin(self.innermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(width,7,day.strftime("%Y"),self.headerfont,self.headerfsize,2)    #year
    self.currentpage.tekst(width - 10,7,day.strftime("%B"),self.headerfont,self.headerfsize,2)     # month
    self.currentpage.tekst(0,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,0)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # thurseday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wdayheight)
    self.currentpage.poporigin()
    self.formfeed()

    self.currentpage.pushorigin(self.outermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(0,7,day.strftime("%Y"),self.headerfont,self.headerfsize,0)    #year
    self.currentpage.tekst(10,7,day.strftime("%B"),self.headerfont,self.headerfsize,0)     # month
    self.currentpage.tekst(width,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,2)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # friday
    self.drawday(day,wdayheight,width)
    day += datetime.date.resolution
    self.currentpage.poporigin()
    self.formfeed()

    self.currentpage.pushorigin(self.innermargin,0)
    # header
    self.currentpage.line(0,self.headerheight - 2,width,0,0,2)
    self.currentpage.tekst(width,7,day.strftime("%Y"),self.headerfont,self.headerfsize,2)    #year
    self.currentpage.tekst(width - 10,7,day.strftime("%B"),self.headerfont,self.headerfsize,2)     # month
    self.currentpage.tekst(0,7,day.strftime("WEEK %W"),self.headerfont,self.headerfsize,0)  # weeknr

    self.currentpage.pushorigin(0,self.headerheight)
    # saturday
    self.drawday(day,wendheight,width)
    day += datetime.date.resolution
    self.currentpage.pushorigin(0,wendheight)
    # sunday
    self.drawday(day,wendheight,width)
    #day += datetime.date.resolution
    self.currentpage.poporigin()
    self.currentpage.poporigin()

  def punchholes(self):
    """ Draw the punch hole on one agenda page
    Using parameter self.nrholes,holestep and holeoffset. This defines just the half of the holes, from the middle.
    Because holes are mirrored to the center. nrholes is the half of the total number of holes, rounded UP
    If holeoffset = 0, just one hole is draw
    """
    # origin is top left of page
    # maybe a parameter which kind of holes 1,2,3,4
    middle = self.agendaheight/2
    if self.currentonevenpage:
      self.currentpage.line(10,middle,5,0,2)
    else:
      self.currentpage.line(self.agendawidth-10,middle,-5,0,2)
    for i in range(self.nrholes):
      hole = i*self.holesstep+self.holesoffset
      if self.currentonevenpage:
        self.currentpage.circle(5,middle+hole,2.75,1,2)    # hole 5.5mm on the left side
        if hole > 0:
          self.currentpage.circle(5,middle-hole,2.75,1,2)
      else:
        self.currentpage.circle(self.agendawidth-5,middle+hole,2.75,1,2)   # holes on the right side
        if hole > 0:
          self.currentpage.circle(self.agendawidth-5,middle-hole,2.75,1,2)

  def drawcutlines(self,paper):
    """
    Draw the line between the agenda pages. The length of the line is from self.cutlinelength.
    The positions are calculated at __init__() from the give papersize. Only the lines at the edge are drawn.

    @param paper: Object pdfout, representing one side of a paper
    @type  paper: L(pdfout.pdfout)
    """
    for x in self.cutlinesx:
      paper.line(x,self.cutlinesy[0]-self.cutlinelength/2,0,self.cutlinelength)
      paper.line(x,self.cutlinesy[-1]-self.cutlinelength/2,0,self.cutlinelength)
    for y in self.cutlinesy:
      paper.line(self.cutlinesx[0]-self.cutlinelength/2,y,self.cutlinelength,0)
      paper.line(self.cutlinesx[-1]-self.cutlinelength/2,y,self.cutlinelength,0)
      
  def formfeed(self):
    """
    Make sure the agenda page is free to be filled, Feed to the next free page. When the physical printer
    paper is full, flush out to file-pdf, and open two empty ones.
    evenpage (page 0) comes before oddpage (page 1), usual people do this the other way round
    """
    # make sure there is a empty page
    if self.currentonevenpage:        # if we are on even page, just change to other side
      self.currentonevenpage = False
      self.currentpage = self.oddpage
      self.oddpage.setorigin(self.oddpageorigins[self.currentagendapage][0],self.oddpageorigins[self.currentagendapage][1])
    else:     # we need a new page
      self.currentonevenpage = True
      self.currentagendapage += 1
      if self.currentagendapage == self.agendapagesperpage:    # check if paper is full
        if self.evenpage != None:
          self.evenpage.save(self.canvas)
        if self.oddpage != None:
          self.oddpage.save(self.canvas)
        self.evenpage = pdfout.pdfout(self.paperwidth,self.paperheight)
        self.drawcutlines(self.evenpage)
        self.oddpage = pdfout.pdfout(self.paperwidth,self.paperheight)
        self.drawcutlines(self.oddpage)
        self.currentagendapage = 0
      self.currentpage = self.evenpage   # start on
      self.evenpage.setorigin(self.evenpageorigins[self.currentagendapage][0],self.evenpageorigins[self.currentagendapage][1])
    self.punchholes()   # should be different, multiple holes are punched..... on same paper, not good

  def assertoddpage(self):
    """ make sure we are on an odd page (left side of agenda)
    Good for starting out with an agenda (eg monday)
    """
    if self.currentonevenpage:
      self.formfeed()
  def assertevenpage(self):
    """ make sure we are on an even page
    Used for the title page
    """
    if not self.currentonevenpage:
      self.formfeed()
      
  def close(self):
    """ write out any object to the pdf-file, and close the pdf stream
    """
    if self.evenpage != None:
      self.evenpage.save(self.canvas)
      self.evenpage = None
    if self.oddpage != None:
      self.oddpage.save(self.canvas)
      self.oddpage = None
    self.canvas.save()

allowedpapers = {
  "A4":reportlab.lib.pagesizes.A4,
  "A3":reportlab.lib.pagesizes.A3,
  "A2":reportlab.lib.pagesizes.A2,
  "A1":reportlab.lib.pagesizes.A1,
  "A0":reportlab.lib.pagesizes.A0,
  "letter":reportlab.lib.pagesizes.letter,
  "legal":reportlab.lib.pagesizes.legal,
  "elevenSeventeen":reportlab.lib.pagesizes.elevenSeventeen,
  "B5":reportlab.lib.pagesizes.B5,
  "B4":reportlab.lib.pagesizes.B4,
  "B3":reportlab.lib.pagesizes.B3,
  "B2":reportlab.lib.pagesizes.B2,
  "B1":reportlab.lib.pagesizes.B1,
  "B0":reportlab.lib.pagesizes.B0}

# width,height,nrholes,offset,distancebetweenholes
agendasizes = {
  'A4':(210,297,2,0,50),    # holes are not good
  'A5':(148,210,3,19,19),     # holes not sure
  'Personal':(95,171,3,23,19),
  'Compact':(95,171,3,0,19),  # holes not sure
  'Pocket':(81,120,3,0,19),   # holes not sure
  'Mini':(67,105,3,0,40)}    # center hole is twice,holes not sure

fonts = (
    "Courier",
    "Courier-Bold"
    "Courier-BoldOblique",
    "Courier-Oblique",
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-BoldOblique",
    "Helvetica-Oblique",
    "Symbol",
    "Times-Bold",
    "Times-BoldItalic",
    "Times-Italic",
    "Times-Roman",
    "ZapfDingbats" )
parser = argparse.ArgumentParser(description='Create a FilofaxDIY printable agenda')
parser.add_argument('--landscape',dest='orient',action='store_const',const='Landscape')
parser.add_argument('--portrait',dest='orient',action='store_const',const='Portrait')
parser.add_argument('--paper',default='letter',choices=allowedpapers)
parser.add_argument('--font',default='Helvetica',choices=fonts)
#parser.add_argument('--filofax',default='Personal',choices=agendasizes)
parser.add_argument('--filofax',default='Personal',choices=('Personal'))
parser.add_argument('--format',default='weekon2pages',choices=('weekon2pages','weekon6pages'))
parser.add_argument('--lineheight',default=4,type=int,choices=range(11))
parser.add_argument('--year',type=int,default=datetime.date.today().year + 1,choices=range(2014,2025))
#parser.add_argument('--language',choices=('en_US.UTF8','nl_NL.UTF8','fy_NL.UTF8'))
parser.add_argument('--language',type=str)

args = parser.parse_args()
if args.orient == None:
  args.orient = 'Portrait'
#print(args)

#-language nl_NL
#of en_US of fy_NL
"""
-Landscape
-Portrait
-paper A4
-font Timesnewroman
&-format weekon2pages | weekon6pages
-lineheight 4
-filofax personal
&-year 2015
"""


#nextyear = datetime.date.today().year + 1
nextnewyearsday = datetime.date(args.year,1,1)
lastmondayofyear = nextnewyearsday - nextnewyearsday.weekday() * datetime.date.resolution

day = lastmondayofyear
outputfilename = "{size}_{year}_{locale}_{format}.pdf".format(size = args.filofax,year = args.year,locale = args.language,format = args.format)
#print(outputfilename)
agenda = filofax(args.language,args.font,args.lineheight,allowedpapers[args.paper],args.orient,outputfilename,agendasizes[args.filofax])
agenda.titlepage(str(args.year))
while day.year <= args.year:
  if args.format == 'weekon2pages':
    agenda.weekon2pages(day)
  else:
    agenda.weekon6pages(day)
  day += datetime.date.resolution * 7
agenda.close()
