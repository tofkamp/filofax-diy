import locale
import datetime
from xfiglib import pdfout
import argparse
from reportlab.pdfgen import canvas
import reportlab.lib.pagesizes
from reportlab.lib.units import cm

FILOFAXDIYVERSION="FilofaxDIY v1.1"

class filofax:
  def __init__(self,language,font,lineheight,paper,orient,filename,filofax):
    if language != None:
      locale.setlocale(locale.LC_TIME,language)
    #statics
    self.font= font
    self.headerfont=self.font
    self.headerfsize=10
    self.headerheight=11
    self.mdayfont=self.font
    self.mdayfsize=19
    self.dayofweekfont=self.font
    self.dayofweekfsize=9

    #self.agendawidth=95.0
    #self.agendaheight=171.0
    self.agendawidth=filofax[0]
    self.agendaheight=filofax[1]
    self.nrholes = filofax[2]
    self.holesoffset = filofax[3]
    self.holesstep = filofax[4]
    self.lineheight = lineheight
    #self.outputfilename = "page{pagenr:04}.fig"
    self.canvas = canvas.Canvas(filename,pageCompression=1,verbosity=0)    #,pagesize=A4,bottumup = 0,pageCompression=0,
    if orient == 'Portrait':
      self.canvas.setPageSize(reportlab.lib.pagesizes.portrait(paper))
    else:
      self.canvas.setPageSize(reportlab.lib.pagesizes.landscape(paper))
    #def __init__(self,filename, pagesize=(595.27,841.89), bottomup = 1, pageCompression=0,
    #               encoding=rl_config.defaultEncoding, verbosity=0  encrypt=None)
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

    self.cutlinelength = 10
    self.outermargin = 5    # margin at the edge
    self.innermargin = 10   # margin at the holes

    """ is now filled with setpaper()
    # the next 5 vars can be derived from papersize and agendapagesize
    self.agendapagesperpage = 3     # xcount =3,ycount=1  count=xcount*ycount
    self.evenpageorigins = [(6.0, 19.5), (101.0, 19.5), (196.0, 19.5)]
    self.oddpageorigins = [(196.0, 19.5), (101.0, 19.5), (6.0, 19.5)]
    self.cutlinesx = (6,101,196,291)
    self.cutlinesy = (19.5,190.5)
    """
    
    self.paperwidth = self.canvas._pagesize[0] * 10 / cm
    self.paperheight = self.canvas._pagesize[1] * 10 / cm
    xcount = int(self.paperwidth / self.agendawidth)
    ycount = int(self.paperheight / self.agendaheight)
    self.agendapagesperpage = xcount * ycount
    startx = (self.paperwidth - xcount * self.agendawidth) / 2.0
    starty = (self.paperheight - ycount * self.agendaheight) / 2.0
    self.cutlinesx = []
    for x in range(xcount + 1):
      self.cutlinesx.append(startx + x * self.agendawidth)
    self.cutlinesy = []
    for y in range(ycount + 1):
      self.cutlinesy.append(starty + y * self.agendaheight)
    self.evenpageorigins = []
    self.oddpageorigins = []
    for y in range(ycount):
      for x in range(xcount):
        self.evenpageorigins.append((self.cutlinesx[x],self.cutlinesy[y]))
      for x in range(xcount-1,-1,-1):
        self.oddpageorigins.append((self.cutlinesx[x],self.cutlinesy[y]))
    
    #dynamic vars
    #self.paperpagenr = 0      # is this still needed ??? page number of outputed paper pages
    self.currentonevenpage = False
    self.currentagendapage = self.agendapagesperpage - 1
    self.evenpage = None
    self.oddpage = None
    self.currentpage = self.evenpage
    
  def titlepage(self,year):
    self.formfeed()
    self.assertevenpage()
    self.currentpage.tekst(self.outermargin+(self.agendawidth-self.innermargin-self.outermargin)/2,self.agendaheight/3,year,self.font,48,1)
    self.currentpage.tekst(self.outermargin+(self.agendawidth-self.innermargin-self.outermargin)/2,self.agendaheight*7/8,FILOFAXDIYVERSION,self.font,12,1)

  def calender(self,year):
    pass

  def monthplanner(self):
    pass

  def drawday(self,day,height,width):
    leftindent = 0
    rightindent = 0
    if self.currentonevenpage:
      # evenpage,holes on left
      self.currentpage.tekst(width,5,str(int(day.strftime("%d"))),self.mdayfont,self.mdayfsize,2)  #day of the month
      self.currentpage.tekst(width - 10,3,day.strftime("%A"),self.dayofweekfont,self.dayofweekfsize,2)  # day of the week
      self.currentpage.tekst(0,3,day.strftime("%j"),self.dayofweekfont,self.dayofweekfsize,0)
      rightindent = 10
    else:
      # oddpage,holes on right
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
    # assert(dayofweek(day) == monday)
    # future collect month names in order to fill header
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
    # maybe parameters for dia,centerfromedge,(distance from middle)
    # origin is top left of page
    # hole will look beter if dot-distance >= 3
    # maybe a parameter which kind of holes 1,2,3,4
    middle = self.agendaheight/2
    if self.currentonevenpage:
      self.currentpage.line(10,middle,5,0,2)
    else:
      self.currentpage.line(self.agendawidth-10,middle,-5,0,2)
    #deltacenterhole = 4
    #betweenholes = 19
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
#self.currentpage.circle(self.agendawidth-5,middle+(i*betweenholes+deltacenterhole),2.75,1,2)   # holes on the right side
#        self.currentpage.circle(self.agendawidth-5,middle-(i*betweenholes+deltacenterhole),2.75,1,2)

  def drawcutlines(self,paper):
    for x in self.cutlinesx:
      paper.line(x,self.cutlinesy[0]-self.cutlinelength/2,0,self.cutlinelength)
      paper.line(x,self.cutlinesy[-1]-self.cutlinelength/2,0,self.cutlinelength)
    for y in self.cutlinesy:
      paper.line(self.cutlinesx[0]-self.cutlinelength/2,y,self.cutlinelength,0)
      paper.line(self.cutlinesx[-1]-self.cutlinelength/2,y,self.cutlinelength,0)
      
  def formfeed(self):
    # make sure there is a empty page
    if self.currentonevenpage:        # if we are on even page, just change to other side
      self.currentonevenpage = False
      self.currentpage = self.oddpage
      self.oddpage.setorigin(self.oddpageorigins[self.currentagendapage][0],self.oddpageorigins[self.currentagendapage][1])
    else:     # we need a new page
      self.currentonevenpage = True
      self.currentagendapage += 1
      if self.currentagendapage == self.agendapagesperpage:
        if self.evenpage != None:
          self.evenpage.save(self.canvas)
        if self.oddpage != None:
          self.oddpage.save(self.canvas)
        self.evenpage = pdfout.pdfout(self.paperwidth,self.paperheight)
        self.drawcutlines(self.evenpage)
        self.oddpage = pdfout.pdfout(self.paperwidth,self.paperheight)
        self.drawcutlines(self.oddpage)
        self.currentagendapage = 0
      self.currentpage = self.evenpage
      self.evenpage.setorigin(self.evenpageorigins[self.currentagendapage][0],self.evenpageorigins[self.currentagendapage][1])
    self.punchholes()

  def assertoddpage(self):
    # make sure we are on an odd page
    if self.currentonevenpage:
      self.formfeed()
  def assertevenpage(self):
    # make sure we are on an even page
    if not self.currentonevenpage:
      self.formfeed()
      
  def close(self):
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
'Mini':(67,105,3,-40,40)}    # center hole is twice,holes not sure

parser = argparse.ArgumentParser(description='Create a FilofaxDIY printable agenda')
parser.add_argument('--landscape',dest='orient',action='store_const',const='Landscape')
parser.add_argument('--portrait',dest='orient',action='store_const',const='Portrait')
parser.add_argument('--paper',default='letter',choices=allowedpapers)
parser.add_argument('--font',default='Helvetica',choices=('Helvetica','Times-Roman'))
parser.add_argument('--filofax',default='Personal',choices=agendasizes)
parser.add_argument('--format',default='weekon2pages',choices=('weekon2pages','weekon6pages'))
parser.add_argument('--lineheight',default=7,type=int,choices=range(11))
parser.add_argument('--year',type=int,default=datetime.date.today().year + 1,choices=range(2014,2025))
parser.add_argument('--language',choices=('en_US.UTF8','nl_NL.UTF8','fy_NL.UTF8'))

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
outputfilename = "Agenda_{year}_{locale}_{format}.pdf".format(year = args.year,locale = args.language,format = args.format)
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
