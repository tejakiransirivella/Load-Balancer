# Networks-Project

This project repository contains the files necessary for implementing a load balancer from scratch using the shortest queue strategy.

## Before the Demo

## Usage

Before and for the demo, the demo was run by using the following JSON configurations:

```json
{
  "server": {
    "count": "1",
    "port_range_start": "50000",
    "port_range_end": "51000",
    "start_id": "0",
    "queue_update_interval": "10"
  },
  "client": {
    "count": "10",
    "port_range_start": "51000",
    "port_range_end": "52000",
    "start_id": "1000"
  },
  "load_balancer": {
    "server_side_port": "54000",
    "client_side_port": "54001",
    "server_scaling_threshold": "5"
  },
  "controller": {
    "port": "55000"
  }
}
```

The demo could be run by running:
python3 controller.py

This printed the client, server, and load balancer initializiations and then periodically prints a table displaying information on the number of servers and how many requests each has according to the load balancer history.
Logs are then ceated displaying information on each server and client.

## After the Demo

We added a graphical display that keeps track of the number of servers running every second.
 
## Usage

The program is run the same as before. The JSON file can be changed to model a more realistic number of clients and servers.

## Link To Demo With Additions

https://youtu.be/dI8UkBEBBmg
  
