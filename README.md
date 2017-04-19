# OCCUR
Occur is the OPeNDAP Citation Creator. It acts as a proxy server, put in between an arbitray OPeNDAP data source and a client requesting data.
Except for citations requests, OCCUR forwards any request from the client to the OPeNDAP data source and passes the response of the data source on to the client.
OCCUR will repsond to the citation request by generating a citation from the DAS (which it requests from the OPeNDAP data source), the subsetting / selection parameters and the time of access.
A citation request is invoked by appending ".citation" to the url of the data source.


## Requirements
The application requires following python packages:

* cherrypy
* requests


## Dockerize
The application can be dockerzied using the included Dockerfile.

Build container:  `docker build . -t occur `

Run the container  `docker run -p 8081:80 occur`


### Container DNS configuration
As of Ubuntu 16.04 and Docker 1.12.6,
containers will fail to set up a DNS server in networks
that block external DNS servers.
The issue is described in: https://github.com/moby/moby/issues/23910
and resolved by

    echo {"dns": ["172.17.0.1"]}  > /etc/docker/daemon.json
    echo listen-address=172.17.0.1 > /etc/NetworkManager/dnsmasq.d/docker-bridge.conf



