# build container
''docker build -t occur .''

# run the container 
''docker run -p 4000:80 occur''

# Container DNS configuration
As of Ubuntu 16.04 and Docker 1.12.6,
containers will fail to set up a DNS server in networks
that block external DNS servers.
The issue is described in: https://github.com/moby/moby/issues/23910 
and resolved by

    echo {"dns": ["172.17.0.1"]}  > /etc/docker/daemon.json &&
    echo listen-address=172.17.0.1 > /etc/NetworkManager/dnsmasq.d/docker-bridge.conf 



