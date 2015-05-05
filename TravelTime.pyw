import urllib.request
import urllib.parse
import xml.dom.minidom
import datetime
import tkinter
import time 
import re
import bs4
import contextlib
import selenium.webdriver 

class TravelTime(tkinter.Frame):
    def __init__(self, master=None):
        master.title('TravelTime')
        master.geometry(("%dx%d")%(300,50))
        tkinter.Frame.__init__(self, master)
        self.pack()
        
        self.message = tkinter.StringVar()
        self.time = tkinter.StringVar()
        
        self.labelMessage = tkinter.Label(master, textvariable=self.message)
        self.labelTime = tkinter.Label(master, textvariable=self.time)
        self.labelMessage.pack()
        self.labelTime.pack()
        
        self.dieFlag = False
        
        # register callback
        self.listenID = self.after(1, self.setLabel)   
    
    def getTravelTimeGoogle(self):
        # Add work and home addresses here
        work = ""
        home = ""

        phantomjs = "phantomjs.exe"
        url = "https://maps.google.com/"
        with contextlib.closing(selenium.webdriver.PhantomJS(phantomjs)) as driver:
            driver.implicitly_wait(10)
            driver.get(url)
            get_directions = driver.find_element_by_id("d_launch")
            start = driver.find_element_by_id("d_d")
            end = driver.find_element_by_id("d_daddr")
            submit = driver.find_element_by_id("d_sub")
            get_directions.click()
            start.send_keys(work)
            end.send_keys(home)
            submit.click()

            content = driver.page_source
            soup = bs4.BeautifulSoup(content)
            route_tag = soup.find(id="altroute_0")

            color_string = route_tag.find('img')['class'][1]
            color_regexp = re.compile("dir-traffic-(.*)")
            color = color_regexp.search(color_string).group(1)

            time_string = route_tag.find(text=re.compile("In current traffic"))
            time_regexp = re.compile("In current traffic:\s*(.*)")
            time = time_regexp.search(time_string).group(1)

        return color, time
        
    def getTravelTimeBing(self):
        # This is the specific url of your directions request to Bing
        url = "" 
        # If you're behind a proxy, you need to uncomment this line, and pass an associative 
        # array into the function, of the form {$protocol : $proxy}
        #
        # proxy_handler = urllib.request.ProxyHandler()
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        data = urllib.request.urlopen(url)
        xmldoc = xml.dom.minidom.parse(data)
        nodelist = xmldoc.getElementsByTagName('TravelDurationTraffic')
        seconds = nodelist.item(0).firstChild.nodeValue
        minutes = int(int(seconds)/60)
        return minutes

    def setLabel(self):
        if(self.dieFlag):
            time.sleep(300)
            die()
            
        #travelTime = self.getTravelTimeBing()
        (color, travelTime) = self.getTravelTimeGoogle()
        if (color == 'green'):
            self.labelTime.config(fg='forest green')
        elif (color == 'yellow'):
            self.labelTime.config(fg='goldenrod')
        elif (color == 'red'):
            self.labelTime.config(fg='red')
            
        self.message.set('Time to home: ')
        self.time.set(str(travelTime))

        hour = datetime.datetime.time(datetime.datetime.now()).hour
        if(hour >= 19 or hour < 8):
            self.labelMessage.config(fg='red')
            self.message.set('YOU SHOULD GO HOME')
            self.time.set('')
            self.dieFlag = True

        self.listenID = self.after(1000*60*5, self.setLabel)
    
root = tkinter.Tk()
TT = TravelTime(root)
TT.mainloop() 
