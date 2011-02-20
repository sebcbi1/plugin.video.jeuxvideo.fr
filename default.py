
import xbmcplugin,xbmcgui,xbmcaddon
import urllib2,urllib,re,os
from BeautifulSoup import BeautifulSoup

__settings__ = xbmcaddon.Addon(id='plugin.video.jeuxvideo.fr')
__home__ = __settings__.getAddonInfo('path')


SITE   = 'http://www.jeuxvideo.fr' 

# plugin handle
HANDLE = int(sys.argv[1])


def getShows():

	content = getUrl(SITE + '/video')
	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.XML_ENTITIES)
	chaines = soup.findAll('div' , {'class' : 'titreChaine'})
	for chaine in chaines:
		url = chaine.a['href']
		img = chaine.a.img['src']
		titre = chaine.a.span.contents[0].encode('utf-8')
		addDir(titre,SITE + url,1, img)

def getEpisodes(dir_url,name):

    	content = getUrl(dir_url)
	
	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.XML_ENTITIES)
	videos = soup.findAll('td' , {'class' : 'video'})

	nb_items = len(videos)

	for video in videos:

		url = video.a['href']
		clip  = getClip(getClipXmlUrl(SITE + url))

		if clip is not None:
			addLink(clip[0],clip[1],clip[2],clip[3],nb_items)   

def getClipXmlUrl(url):
	# http://www.jeuxvideo.fr/video/carrement-jeux-video/video-carrement-jeux-video-1-wwe-all-stars-marvel-vs-capcom-3-et-top-5-jeux-de-plateforme-372066.html
	id = re.search(r'.+\-(.+?)\.html',url).group(1)
	# http://www.jeuxvideo.fr/api/tv/xml.php?player_generique=player_generique&id=372066
	return "http://www.jeuxvideo.fr/api/tv/xml.php?player_generique=player_generique&id=%s" % id

def getClip(url):

	content = getUrl(url)
	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.XML_ENTITIES)

	item = soup.find('item')
	title = item.title.contents[0].encode('utf-8').strip()
	try: descr = item.description.contents[0].encode('utf-8').strip()
	except: descr = ''
	mp4 = item.url_video_sd.contents[0].strip()
	if __settings__.getSetting('hq') == 'true':
		try: mp4 = item.url_video_hq.contents[0].strip()
		except: pass
	img = item.visuel_clip.contents[0].strip()
	return [title,mp4,img,descr]

def get_params():

	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	
	return param


def addLink(name,url,iconimage,description,nb_items):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot" : description } )
	ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=url,listitem=liz, totalItems=nb_items)
	return ok



def addDir(name,url,mode,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz,isFolder=True)
	return ok


def getUrl(url):
	req = urllib2.Request(url)
	req.addheaders = [('Referer', SITE), ('Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13')]
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link


params=get_params()
url=None
name=None
mode=None

try:
		url=urllib.unquote_plus(params["url"])
except:
		pass
try:
		name=urllib.unquote_plus(params["name"])
except:
		pass
try:
		mode=int(params["mode"])
except:
		pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
	print ""
	getShows()
	
elif mode==1:
	print ""+url
	getEpisodes(url,name)

xbmcplugin.endOfDirectory(HANDLE)	

