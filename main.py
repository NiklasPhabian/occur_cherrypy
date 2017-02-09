import requests
import cherrypy
from citation import Citation

localhost = 'http://127.0.0.1:8080/opendap/'

class Occur:
    exposed = True

    def GET(self, *args, **kwargs):
        """
        Overwrites the GET method
        :param args: arguments before '?' (separated by '/')
        :param kwargs: arguments after '?' (separated by ';')
        :return: either citation, html or data
        """
        print(cherrypy.request.params)

        ext = None
        if len(args):
            ext = args[-1].split('.')[-1]

        if 'css' in args or 'images' in args:
            return self.fetch_opendap_response()
        elif 'opendap_url' in cherrypy.request.params:
            self.set_opendap_url()
            if kwargs and '/citation' in list(kwargs)[0]:
                # We return subset citation if 'citation' in kwargs (after ?)
                return self.subset_citation()
            elif 'citation' in args:
                # We return whole citation if 'citation' in args (before ?)
                return self.dataset_citation()
            elif ext == 'das' or ext == 'dds' or ext =='ascii' or ext == 'nc':
                return self.fullpage()
            else:
                return self.frameset()
        elif 'opendap_url' in cherrypy.session:
            path = cherrypy.request.path_info
            if len(cherrypy.request.query_string) > 0:
                redirect = path + '?' + cherrypy.request.query_string + ';opendap_url=' + cherrypy.session['opendap_url']
            else:
                redirect = path + '?opendap_url=' + cherrypy.session['opendap_url']
            print(redirect)
            raise cherrypy.HTTPRedirect(redirect)
        else:
            return self.config()

    def das(self):
        das_request = self.trimmed_requestline() + '.das'
        ret = requests.get(das_request)
        return ret.text

    def dataset_citation(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        citation = Citation()
        citation.from_das(self.das())
        citation.dict['url'] = self.trimmed_requestline() + '.html'
        return citation.as_text()

    def subset_citation(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        citation = Citation()
        citation.from_das(self.das())
        citation.dict['url'] = self.trimmed_requestline() + '.html'
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
        request_line = self.opendap_request_line()
        request_line = request_line.replace('/citation', '')
        request_line = request_line.replace('.ascii', '')
        request_line = request_line.replace('.html', '')
        request_line = request_line.replace('.das', '')
        request_line = request_line .split('?')[0]
        return request_line

    def fullpage(self):
        main = self.modified_opendap_response()
        return main

    def frameset(self):
        main = self.modified_opendap_response()

        with open('frame.html') as template:
            html = template.read()
        html = html.replace('${main_msg}', main)
        html = html.replace('${top_msg}', self.top_frame())
        return html

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
            html = html.replace('document.forms[0]', 'document.forms[1]')
            html = html.replace(cherrypy.session['opendap_url'], localhost)
            return html
        else:
            return opendap_response.text

    def fetch_opendap_response(self):
        opendap_url = self.opendap_request_line()
        ret = requests.get(opendap_url)
        return ret

    def top_frame(self):
        form = """This is OCCUR. Currently using following OPeNDAP Server:
                        <form method="get">
                            <input type="text" size=40 value="{opendap_url}" name="opendap_url" action=set_opendap_url/>
                            <button type="submit">launch</button>
                        </form>
                """.format(opendap_url=cherrypy.session['opendap_url'])
        return form

    def config(self):
            return """
              <body>
                <form method="get">
                  <input type="text" size=40 value="http://opendap.jpl.nasa.gov:80/opendap" name="opendap_url"/>
                  <button type="submit">launch</button>
                </form>
              </body>
            """

    def set_opendap_url(self):
        opendap_url = cherrypy.request.params['opendap_url']
        cherrypy.session['opendap_url'] = opendap_url

    def opendap_request_line(self):
        base = cherrypy.session['opendap_url']
        path = cherrypy.request.path_info
        path = path.replace('opendap/', '')
        cherrypy.request.params.pop('opendap_url', None)
        query = '?' + ','.join(list(cherrypy.request.params))

        request_line = base + path + query
        return request_line


if __name__ == '__main__':
    conf = {'/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.sessions.on': True}
    }
    cherrypy.config.update("server.conf")
    cherrypy.tree.mount(Occur(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
