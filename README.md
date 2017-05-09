# BTAid

A Python/Raspberry Pi project to assist visually impaired riders on the Blacksburg Transit system.

### Hardware Requirements
* Raspberry Pi 3 model B (at least 2)
* Speakers (USB/3.5mm)
* Estimote Proximity Beacons
* Optional: Raspberry Pi compatible battery pack

### Software Requirements/Installation
##### Server Pi:
* Python 3.5 or newer
* [RabbitMQ](https://www.rabbitmq.com/install-debian.html) (requires configuring a new virtual host, user, and password)
* MongoDB:  
`sudo apt-get install mongodb`
* Python modules:  
`sudo pip3 install requests pymongo pika`

##### Client Pis:
* Python 3.5 or newer
* Flite:  
`sudo apt-get install flite`
* BLE dependencies:  
`sudo apt-get install pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev libcap2-bin python-dev`
* Grant Python permission to access sockets:  
`sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python))`
* PyBluez with Bluetooth Low Energy support:  
`sudo pip3 install pybluez[ble]`
* BeaconTools with scanning support:  
`sudo pip3 install beacontools[scan]`
* Additional Python modules:  
`sudo pip3 install pika uuid twilio`

### Usage

1. On the server, run `ifconfig` and note the IPv4 address (inet addr under wlan0)
2. Server: `sudo python3 server.py -b server IP address`
3. Clients: `sudo python3 client.py -b server IP address`

### Project Demonstration
<a href="http://www.youtube.com/watch?feature=player_embedded&v=ajcvdMd9TQk
" target="_blank"><img src="http://img.youtube.com/vi/ajcvdMd9TQk/0.jpg" 
alt="Click here to watch on YouTube" width="240" height="180" border="10" /></a>