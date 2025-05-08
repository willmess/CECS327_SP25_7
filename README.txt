
CECS 327 - Assignment 8: End-to-End IoT System
==============================================

Team Members: Shane Kerr, William Messick
Platform: Google Cloud VMs
Submission: Spring 2025

Overview
--------
This project implements a fully integrated IoT system with the following components:

- TCP Server: Accepts IoT-related queries, connects to NeonDB Data_virtual table, processes sensor data, and returns results.
- TCP Client: Sends natural-language queries to the server and displays processed responses.
- IoT Sensor Data: Simulated via Dataniz.com and stored in NeonDB.
- Metadata Tree: Device metadata is stored and accessed via a Binary Search Tree (BST).
- Unit Conversions: Converts sensor data to RH%, gallons, and kWh; all timestamps returned in PST.

Architecture & Deployment
--------------------------
Client VM:
  - Google Cloud Windows Server VM used to run client.py using python

Server VM:
  - Separate Google Cloud VM running server.py
  - Connected to NeonDB
  - Custom firewall rule added to allow traffic on TCP port 5555

Communication:
  - Internal IP + port 5555 used for VM-to-VM messaging

Database:
  - PostgreSQL instance hosted on NeonDB
  - Sensor data stored in "Data_virtual" table (case-sensitive)

Files
-----
- client.py: TCP client that sends one of three predefined queries
- server.py: TCP server that connects to NeonDB, processes JSON payload, uses BST for metadata, returns converted results

Supported Queries
-----------------
1. What is the average moisture inside my kitchen fridge in the past three hours?
2. What is the average water consumption per cycle in my smart dishwasher?
3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?

How to Run
----------

SERVER (on the server VM):
---------------------------
1. Start windows server vm
2. In server vm open terminal and navigate to the project directory
3. Run:
   python server.py
4. When prompted, enter:
   IP address: 0.0.0.0
   Port: 5555

CLIENT (on the client VM):
---------------------------
1. Run windows client vm
2. In client vm open terminal and navigate to the project directory
2. Run:
   python client.py
3. When prompted, enter:
   IP address: internal IP of the server VM(external won't look)
   Port: 5555
4. Choose and enter one of the three valid queries when prompted

Database Details
----------------
Table: "Data_virtual" (case-sensitive with capital D)

Example Payload:
{
  "timestamp": "1745362203",
  "topic": "Fridge/Board/Sensor",
  "board_name": "Fridge Pi",
  "Moisture Meter - MoistMeter": "18.1340"
}

Networking Notes
----------------
- Firewall rule created to allow incoming TCP traffic on port 5555 to the server VM
- VMs communicate using internal IP for security and performance

Dependencies
------------
Install with:

  pip install psycopg2-binary python-dateutil pytz

