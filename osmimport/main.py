# read and write favorites.gpx of the osmandmaps app on my iPhone
from lxml import etree as LT
from lxml.builder import E
from lxml.etree import tostring


# lookup the wpt in the mergeDoc, return true if present
def lookForInMergeWpt(mergeDoc, wpt):
    lat = wpt.get('lat')
    lon = wpt.get('lon')
    xpath = 'wpt[round(@lat*10000)=round(number(' + lat + ')*10000) and round(@lon*10000)=round(number(' + lon + ')*10000)]'
    foundWpt = mergeDoc.xpath(xpath)
    return foundWpt


def generateWpts(wpts, nsmap, resultFilename):
# xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
#    gpxName = '{http://www.topografix.com/GPX/1/1}gpx'
    gpxName = 'gpx'
    gpxList = LT.Element(gpxName)
    for wpt in wpts:
        gpxList.append(wpt)

    xmlStr = tostring(gpxList, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    outfile = open(resultFilename, "w")
    s = xmlStr.decode('utf-8')
    a = outfile.write(s)
    outfile.close()


def merge(mergeFilename, mainFilename, resultFilename):
    mergeDoc = LT.parse(mergeFilename)
    mainDoc = LT.parse(mainFilename)

    mergeRoot = mergeDoc.getroot()
    mainRoot = mainDoc.getroot()

    wpts = []
    for wpt in mainRoot:
        # Only copy wpt if it is not present in the mergefile
        # thus removing old instances of wpt if present
        mergeWpt = lookForInMergeWpt(mergeDoc, wpt)
        if len(mergeWpt) == 0:
            wpts.append(wpt)
        else:
            wpts.append(mergeWpt[0])

    # Copy the content of the mergefile to the wpts
    for wpt in mergeRoot:
        wpts.append(wpt)

    generateWpts(wpts, mainRoot.nsmap, resultFilename)


# merge minibiebs.xml from favourites.gpx to GFG1.gpx
merge('minibiebs.xml', 'favourites_org.gpx', 'GFG1.xml')

# read xml from file, sort records using XSLT
dom = LT.parse('GFG1.xml')
xslt = LT.parse('process.xslt')
transform = LT.XSLT(xslt)
newdom = transform(dom)
b = bytes(newdom)

outfile = open("favourites.xml", "w")
s = b.decode('utf-8')
a = outfile.write(s)
outfile.close()
