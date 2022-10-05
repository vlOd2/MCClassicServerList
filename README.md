# MCClassicServerList
A simple server list for Minecraft Classic servers

# What is MCClassicServerList
A server list software written in Python for Minecraft Classic servers

# The source code! It's yucky
This project was originally intended as a joke and a challenge for my self, but I managed to make this fully fledged<br>
I will revisit and recreate it from scratch but for now this is what you have to use

# How do I use it?
For this step you should have a domain registered and opened the TCP port you specified in the config<br>
If you don't have a domain you can replace url with "http://[your public ip]" (you can get your ip by going to http://icanhazip.com/)<br>
If people outside your network can't access your list, make sure your listen port is opened, some isps block the default port used and port forwarding entirely! (you can use https://www.yougetsignal.com/tools/open-ports/ to check)

1. Download python from https://www.python.org/downloads/
2. Download MCClassicServerList.py from this repository
3. Edit the settings listed bellow in MCClassicServerList.py:
```
listenip = "0.0.0.0"
listenport = 80
clean_timeout = 120
url = "http://localhost:<same value as listenport>"

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
You have to use a proxy in order for the server to connect to the list!<br>
The following steps use "Telerik Fiddler" as the proxy as it's the easiest to use<br><br>
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
5. Click "Save Script" and minimize Fiddler (do not close it as the server will fail to connect to the proxy)
6. Now go to your server run script command and add `-Dhttp.proxyHost=127.0.0.1 -Dhttp.proxyPort=8888` after java, your run command should look something simillar to this: `java.exe -Dhttp.proxyHost=127.0.0.1 -Dhttp.proxyPort=8888 -cp minecraft-server.jar com.mojang.minecraft.server.MinecraftServer`
7. Download the MPPASS patch from releases (it's called i.class) and open your server jar with [7-Zip](https://7-zip.org) (or a familliar program) and navigate to com/mojang/minecraft/server and drag and drop the download "i.class" file (backup your jar first)
8. Run your server
9. Enjoy

# It's not working! Where can I get help?
You can create a new issue in the "Issues" tab
