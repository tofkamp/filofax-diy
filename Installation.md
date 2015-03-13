# Introduction #

How-to create your own FilofaxDIY printable agenda

# Details #

install python

install reportlab pdf generator

install your locale with `dpkg-reconfigure locales`


Run the script:
```
python filofaxDIY.py --year 2015 --language en_US.UTF8
```
In the current directory, you will find a pdf file which you can print.

Other examples:
```
python filofaxDIY.py --font Helvetica --language nl_NL.UTF8 --paper letter --portrait --weekon6pages
```
```
python filofaxDIY.py --font Times-Roman --language fy_NL.UTF8 --paper A3 --landscape --weekon2pages --lineheight 0
```

# See also #

[Printing](Printing.md)