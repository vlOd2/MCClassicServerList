# MCClassicServerList
A simple server list for Minecraft Classic servers

# What is MCClassicServerList
A server list software written in Python for Minecraft Classic servers

# The source code! It's yucky
This project was originally intended as a joke and a challenge for my self, but I managed to make this fully fledge<br>
I will revisit and recreate it from scratch but for now this is what you have to use

# How do I use it?
1. Download python from https://www.python.org/downloads/
2. Download MCClassicServerList.py from this repository
3. Edit the settings listed bellow in MCClassicServerList.py:
```
listenip = "0.0.0.0"
listenport = 80
clean_timeout = 120
url = "http://localhost"

note: these are the defaults in case you mess up
```
4. Run MCClassicServerList in a console window with `py MCClassicServerList.py` (make sure you are in the right directory!)
5. Done (if you want to quit press Ctrl + C)

# How do I use online verification?
1. Create an user account by visiting `<url>/api/create_account?username=<username>&password=<password>` (change the values marked with <> to your liking)
2. Make sure your server is in the list!
3. Get the MPPASS by visiting `<url>/api/mppass?username=<username>&password=<password>&serverip=<server's ip>&serverport=<server's port>` (change the values marked with <> to your liking)
4. You may now use the MPPASS to connect to the server (Make sure the USERNAME matches the one used in the request as IT IS CASE SENSITIVE)

# How do I make my vanilla server connect to the list?
1. Download [Telerik Fiddler](https://telerik-fiddler.s3.amazonaws.com/fiddler/FiddlerSetup.exe)
2. Go to File (top menu) and uncheck "Capture Traffic"
3. Go to "FiddlerScript" from the top of the right section
4. Delete everything in there and paste the following script (make sure to replace the url with your own one, DO NOT INCLUDE THE SCHEME):
```
import System;
import System.Windows.Forms;
import Fiddler;

class Handlers
{
    static function OnBeforeRequest(oSession: Session) {
        if (oSession.hostname.Contains("minecraft.net")) {
            if (oSession.PathAndQuery.Contains("/heartbeat.jsp")) {
                oSession.hostname = "<url>";
                oSession.PathAndQuery = "/heartbeat";
            }    
        }
    }

    static function OnBeforeResponse(oSession: Session) {
    }
}
```
5. Click "Save Script"
6. Now go to your server run script command and add `-Dhttp.proxyHost=127.0.0.1 -Dhttp.proxyPort=8888` after java, your run command should look like this:
