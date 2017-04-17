import cherrypy
import requests
from citation import Citation


# This is the opendap server we are fetching from
opendap_server = 'http://opendap.jpl.nasa.gov:80/opendap'

# This is the configuration of our OCCUR server
localhost = 'http://127.0.0.1:8080/opendap/'


class Occur:
    exposed = True

    def GET(self, *args, **kwargs):
        """
        Overwrites the GET method
        :param args: arguments before '?' (separated by '/')
        :param kwargs: arguments after '?' (separated by ',')
        :return: either citation, html or data
        """
        print(args)
        if kwargs and '/citation' in list(kwargs)[0]:
            # We return subset citation if 'citation' in kwargs (after ?)
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            return self.subset_citation()
        elif 'citation' in args:
            # We return whole citation if 'citation' in args (before ?)
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            return self.dataset_citation()
        else:
            # We pass through the modified OPeNDAP server response
            return self.modified_opendap_response()

    def modified_opendap_response(self):
        """
        Fetch the response from the opendap server
        :return: opendap response (html incl. header)
        """
        opendap_response = self.fetch_opendap_response()
        cherrypy.response.headers['Content-Type'] = opendap_response.headers['Content-Type']
        if opendap_response.headers['Content-Type'] == 'text/html':
            # If the response is an HTML, we bend references to our server
            html = opendap_response.text
            html = html.replace(opendap_server, localhost)
            return html
        else:
            return opendap_response

    def fetch_opendap_response(self):
        opendap_url = self.request_line()
        return requests.get(opendap_url)

    def request_line(self):
        base = opendap_server
        path = cherrypy.request.path_info
        request_line = base + path
        return request_line

    def dataset_citation(self):
        citation = Citation()
        citation.from_das(self.das())
        citation.dict['url'] = opendap_server + self.trimmed_requestline() + '.html'
        return citation.as_text()

    def subset_citation(self):
        citation = Citation()
        citation.from_das(self.das())
        citation.dict['url'] = opendap_server + self.trimmed_requestline() + '.html'
        citation.add_subset_param_dict(self.subset_params())
        return citation.as_text()

    def subset_params(self):
        params = list(cherrypy.request.params)[0].split('/')[0]
        params = params.split(',')
        params_dict = {}
        for param in params:
            key = param.split('[')[0]
            value = '[' + param.split('[')[1]
            params_dict[key] = value
        return params_dict

    def trimmed_requestline(self):
        request_line = self.request_line()
        request_line = request_line.replace('/citation', '')
        request_line = request_line.replace('.ascii', '')
        request_line = request_line.replace('.html', '')
        request_line = request_line.replace('.das', '')
        return request_line

    def das(self):
        das_request = (opendap_server + self.trimmed_requestline()).split('?')[0] + '.das'
        ret = requests.get(das_request)
        return ret.text



class OccurTest:
    def __index__(self):
        pass


if __name__ == '__main__':
    conf = {'/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
                }
            }
    cherrypy.tree.mount(Occur(), '/', conf)
    cherrypy.tree.mount(OccurTest(), '/config', conf)

    cherrypy.engine.start()
    cherrypy.engine.block()
