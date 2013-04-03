import urllib, xml.dom.minidom, xbmc
  
def GetStringFromUrl(encurl):
    doc = ""
    succeed = 0
    while succeed < 5:
        try: 
            f = urllib.urlopen(  encurl)
            doc = f.read()
            f.close()
            return str(doc)
        except:
            log("could not get data from %s" % encurl)
            succeed = succeed + 1

def GetValue(node, tag):
    v = node.getElementsByTagName(tag)
    if len(v) == 0:
        return '-'
    
    if len(v[0].childNodes) == 0:
        return '-'
    
    return unicode(v[0].childNodes[0].data)

def GetAttribute(node, attr):
    v = unicode(node.getAttribute(tag))
    
def Notify(header, line='', line2='', line3=''):
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)' % (header, line, line2, line3) )