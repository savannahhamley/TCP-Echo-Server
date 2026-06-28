This program utilizes a container where PROXY_PORT (mapped to 25297) serves as the host entry point, allowing external traffic from clients to reach the server container. The SERVER_PORT (8529) is the internal port on which the server application listens.

Running and Scaling Instructions:

1.	To set up the environment, execute docker-compose up -d to initialize the bridge network and containers.
2.	To initialize the server, execute docker exec -it csci-server-hamley python3 server.py to start the multi-threaded server process.
3.	To add multiple users, open separate terminal windows and execute docker exec -it csci-client-hamley python3 client.py in each. This allows multiple clients to establish independent TCP sessions on one central server.
