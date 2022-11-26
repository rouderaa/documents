# Making a GET request
import requests
import re
import json

fromWeb = False
def collectdata(city):
    print("collecting data for : %s." % (city))
    filename = "minibiebs_" + city + ".txt"
    if fromWeb:
        url = 'https://minibieb.nl/?s='+city+'&geo-radius=280&geo-lat=0&geo-lng=0&categories=0&locations=0&dir-search=yes'
        r = requests.get(url)
        s = r.content.decode('utf-8')
        textFile = open(filename, "w")
        textFile.write(s)
        textFile.close()
    else:
        textFile = open(filename, "r")
        # textFile.write(s)
        s = textFile.read()
        textFile.close()
    return s


def generateMinibiebData(htmlData):
    # Possible data parsing states
    SCAN = 0
    INSIDEVALUES = 1
    OUTSIDEVALUES = 2
    INSIDEDATA = 3
    INSIDEOPTIONS = 4

    # String parsing states
    OUTSIDETERM = 0
    INSIDETERM = 1
    INSIDEDOUBLESTRING = 2
    INSIDESINGLESTRING = 3
    DONE = 4
    INSIDEESCAPEDDOUBLESTRING = 5

    state = SCAN
    quoteState = OUTSIDETERM
    line = ''
    singleLine = ''
    body = ''
    for ch in htmlData:
        # add double quotes around literals and not around strings
        if quoteState == OUTSIDETERM:
            if ch.lower() >= 'a' and ch.lower() < 'z':
                line = line + '"'
                quoteState = INSIDETERM
            if ch == '"':
                quoteState = INSIDEDOUBLESTRING
            if ch == "'":
                quoteState = INSIDESINGLESTRING
        elif quoteState == INSIDETERM:
            if not (ch.lower() >= 'a' and ch.lower() < 'z'):
                line = line + '"'
                quoteState = OUTSIDETERM
        elif quoteState == INSIDEDOUBLESTRING:
            if ch == '\n':
                ch = ''
            if ch == '&':
                ch = '&amp;'
            if ch == '\\':
                ch = ''
                quoteState = INSIDEESCAPEDDOUBLESTRING
            if ch == '"':
                quoteState = OUTSIDETERM
        elif quoteState == INSIDEESCAPEDDOUBLESTRING:
            ch = ''
            quoteState = INSIDEDOUBLESTRING
        elif quoteState == INSIDESINGLESTRING:
            if ch == '\n':
                ch = ''
            if ch == "'":
                quoteState = OUTSIDETERM

        line = line + ch
        if ch == '\n':
            line = line.replace('<br >', ' ')
            line = line.replace('<br>', ' ')
            if state == SCAN:
                if re.search(r"\"values\":", line) is not None:
                    body = line
                    state = INSIDEVALUES
            elif state == INSIDEVALUES:
                if re.search(r"\"events\":", line) is not None:
                    line = ''
                    body = body[:-2]
                    body = body + "\n\t\t\t\t]"
                    state = DONE
                if re.search(r"\"options\":", line) is not None:
                    line = ''
                    skipNrOfLines = 3
                    state = INSIDEOPTIONS
                if re.search(r"\"data\":", line) is not None:
                    data = line
                    line = ''
                    state = INSIDEDATA
                if re.match(r"			\"options\":", line) is not None:
                    # remove last two characters
                    body = body[:-2]
                    state = OUTSIDEVALUES
                else:
                    body = body + line
            elif state == INSIDEOPTIONS:
                skipNrOfLines = skipNrOfLines - 1
                if skipNrOfLines == 0:
                    state = INSIDEVALUES
            elif state == INSIDEDATA:
                # extract the title
                result = re.search(r'title..+"([^"]+)"', line)
                if result is not None:
                    title = result.group(1)
                    body = body + "\t\t\t\t\t\t\"title\": \"" + title + "\",\n"
                # extract the address
                result = re.search(r'address..+"([^"]+)"', line)
                if result is not None:
                    address = result.group(1)
                    address = address.replace(r"<br \/>\n", ",")
                    body = body + "\t\t\t\t\t\t\"address\": \"" + address + "\"\n"
                # check for end of data
                if re.search(r"},", line) is not None:
                    body = body + "\t\t\t\t\t},\n"
                    state = INSIDEVALUES

            line = ''

    # Add curly brackets to make it JSON again
    body = '{' + body + ' \n}'

    # store body for debugging json
    bodyFile = open("body.txt", "w")
    bodyFile.write(body)
    bodyFile.flush()
    bodyFile.close()

    # Parse json into a dictionary
    json_dicti = json.loads(body)

    elements = json_dicti['values']
    return elements

def convertToXml(elements):
    # Loop along dictionary
    xml = ""
    for element in elements:
        xml = xml + '<wpt lat="%f" lon="%f">' % (element['latLng'][0], element['latLng'][1])
        # <icon>tourism_information</icon>
        # <icon>special_star</icon>
        xml = xml + '<name>%s</name><extensions><icon>tourism_information</icon><background>circle</background><color>#3cb371</color><address>%s</address></extensions>' % (
            element['title'], element['address'])
        xml = xml + '</wpt>'
    return xml

# Generate minibiebs.xml file
xml = '<?xml version="1.0"?>'
# xml = xml + '<gpx version="1.1" creator="OsmAnd" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" >'
xml = xml + '<gpx version="1.1" creator="OsmAnd" >'

cities = ["utrecht", "amersfoort", "barneveld", "leusden", "soest", "nijkerk", "baarn", "woudenberg", "zeist", "hilversum", "bunschoten", "hoevelaken", "terschuur", "zwartebroek" ]
# cities = ["barneveld"]
for city in cities:
    htmlData = collectdata(city)
    elements = generateMinibiebData(htmlData)
    xml = xml + convertToXml(elements)
    print("Found %d minibiebs for city %s\n" % (len(elements), city))

xml = xml + '</gpx>'

# Store total xml data in file
outfile = open("minibiebs.xml", "w")
a = outfile.write(xml)
outfile.close()
