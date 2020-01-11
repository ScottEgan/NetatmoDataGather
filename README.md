# Netatmo Database and Graph Visualization

### Using:

- Raspberry Pi
- Netatmo API
- InfluxDB
- Grafana  

This is a tutorial for setting up a Raspberry Pi to fetch and store Netatmo weather station data in a InfluxDB database while also displaying the database information with Grafana on a kiosk style screen  
fetchAndWriteData.py was adapted from: https://gist.github.com/arnesund/29ffa1cdabacabe323d3bc45bc7db3fb

## 1. Install Rasbian and Configure Pi

There are thousands of tutorials out there on how to do this. Google it and find one with the level of detail your experience requires. Here are the basic steps (mostly so I can remember):

1. Use balenaEtcher to prepare SD card with latest full version of Rasbian
2. Plug in networking, monitor, keyboard and power
3. Log in with user: pi password: raspberry
4. Change password
5. Expand file system
6. Turn on SSH  
7. ```sudo reboot```  
8. ```sudo apt update```  
9. ```sudo apt upgrade```  


## 2. Sign up for Netatmo App

You will need a ID and Key from Netatmo in order to use their API.

1. Go to [https://dev.netatmo.com/apps/createanapp](https://dev.netatmo.com/apps/createanapp) and follow the steps to sign up
2. Find your client ID and your client secret
3. Look through the documentation. [https://dev.netatmo.com/apidocumentation/weather](https://dev.netatmo.com/apidocumentation/weather)

## 3. Install InfluxDB

1. Follow most of this tutorial [https://pimylifeup.com/raspberry-pi-influxdb/](https://pimylifeup.com/raspberry-pi-influxdb/)
2. In the **Using InfluxDB on your Raspberry Pi** section only do steps 1 and 2
  1. Create a database using step 2 and name it whatever you want, just remember this name
3. Go to the **Adding Authentication to InfluxDB** section and do all steps
4. Now you should have an influx database up and running that will start on reboot

## 4. Write a script to handle the data

1. See fetchAndWriteData.py [here](https://github.com/ScottEgan/NetatmoDataGather)
2. I think netatmo stores data every 10min so set code to run every 8
   - [https://www.raspberrypi.org/documentation/linux/usage/cron.md](https://www.raspberrypi.org/documentation/linux/usage/cron.md)
   - Use cron: ```*/8 \* \* \* \* /home/pi/fetchAndWriteData.py >> /home/pi/netatmoLogs.txt```
  
## 5. Install Grafana

1. Follow [https://pimylifeup.com/raspberry-pi-grafana/](https://pimylifeup.com/raspberry-pi-grafana/)
2. Connect InfluxDB using default settings and your username and password from when you installed influx

## 6. Configure Grafana Dashboard

1. Play around with the queries and visualizations until you get something you are happy with
2. If you download a plugin you will need to restart the server with:

   - ```systemctl restart grafana-server```

1. Set the home dashboard in Configuration\&gt;Preferences\&gt;Home Dashboard

## 7. Set Grafana to start in kiosk mode at startup

1. Use instructions from here [https://github.com/grafana/grafana-kiosk](https://github.com/grafana/grafana-kiosk)
2. Use wget to grab the tar file from releases section  
   1. Find URL of latest release gz  
   2. ```wget URL```  
   3. Extract the tar file with ```tar xvzf <path/to/tar.gz>```  
2. Pick a way to do automatic startup
   1. I used the Systemd startup option [https://github.com/grafana/grafana-kiosk#systemd-startup](https://github.com/grafana/grafana-kiosk#systemd-startup)
   2. Use the first two commands to create the file and edit permissions
   3. Then add the next block of code to the file using a text editor
     1. Make sure to personalize the ```ExecStart=``` section based on what you want to see and which options you want to use
   4. Follow the rest of the instructions in that section

That should be everything

References:  
[https://arnesund.com/2016/07/10/visualize-your-netatmo-data-with-grafana/](https://arnesund.com/2016/07/10/visualize-your-netatmo-data-with-grafana/)  
[https://grafana.com/docs/grafana/latest/plugins/installation/](https://grafana.com/docs/grafana/latest/plugins/installation/)
