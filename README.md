# occur
Occur is the OPeNDAP Citation Creator. It acts as a proxy server, put in between an arbitray OPeNDAP data source and a client requesting data.
Except for citations requests, occur forwards any request from the client to the OPeNDAP data source and passes the response of the data source on to the client.
A citation request is invoked by appending ".citation" to the url of the data source. Occur will repsond to the citation request by generating a citation from the DAS (which it requests from the OPeNDAP data source), the subsetting / selection parameters and the time of access.

Occur is built with, and hence depends on cherrypy and requests.

