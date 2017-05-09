import requests
import cherrypy
from citation import Citation
import configparser

config = configparser.ConfigParser()
config.read('server.conf')
host = config['global']['server.socket_host'].replace('\'','')
port = config['global']['server.socket_port']
local_host = 'http://' + host + ':' + port + '/opendap'

class Occur:
    exposed = True

    def GET(self, *args, **kwargs):
        """
        Overwrites the GET method.
        Returns either citation, html or data
        
        Keyword arguments:
        param args: arguments before '?' (separated by '/')
        param kwargs: arguments after '?' (separated by ';')        
        """        
        ext = None
        if len(args):
            ext = args[-1].split('.')[-1]

        if 'css' in args or 'images' in args:
            return self.fetch_opendap_response()
        elif 'opendap_url' in cherrypy.request.params:
            self.set_opendap_url()            
            if ext == 'das' or ext == 'dds' :                
                return self.fullpage()
            elif ext =='ascii':
                return self.ascii_response()
            elif ext == 'nc' or ext == 'nc4' or ext == 'dods':
                return self.file_response()                
            elif ext =='citation':                
                return self.citation()
            else:
                return self.frameset()
        elif 'opendap_url' in cherrypy.session:            
            path = cherrypy.request.path_info
            if len(cherrypy.request.query_string) > 0:
                redirect = path + '?' + cherrypy.request.query_string + ';opendap_url=' + cherrypy.session['opendap_url']
            else:
                redirect = path + '?opendap_url=' + cherrypy.session['opendap_url']            
            raise cherrypy.HTTPRedirect(redirect)
        else:            
            return self.config()

    def das(self):
        das_request = self.trimmed_requestline() + '.das'
        ret = requests.get(das_request)
        return ret.text

    def citation(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        citation = Citation()
        citation.from_das(self.das())
        citation.meta['url'] = self.trimmed_requestline() + '.html'
        citation.add_subset_param_dict(self.subset_params())
        return citation.as_text()

    def subset_params(self):        
        params_dict = {}
        print(self.opendap_request_line())
        if len(cherrypy.request.params)>0:            
            params = list(cherrypy.request.params)[0].split('/')[0]            
            params = params.split(',')            
            for param in params:
                key = param.split('[')[0]
                value = '[' + param.split('[')[1]
                params_dict[key] = value        
        return params_dict

    def trimmed_requestline(self):
        request_line = self.opendap_request_line()
        request_line = request_line.replace('.citation', '')
        request_line = request_line.replace('.ascii', '')
        request_line = request_line.replace('.html', '')
        request_line = request_line.replace('.das', '')
        request_line = request_line .split('?')[0]
        return request_line

    def fullpage(self):
        main = self.get_opendap_response()
        return main

    def frameset(self):
        main = self.html_response()
        with open('frame.html') as template:
            html = template.read()
        html = html.replace('${main_msg}', main)
        html = html.replace('${top_msg}', self.top_frame())
        return html

    def get_opendap_response(self):
        """
        Fetch the response from the opendap server and return opendap response (html incl. header)                
        """
        opendap_response = self.fetch_opendap_response()
        cherrypy.response.headers['Content-Type'] = opendap_response.headers['Content-Type']
        return opendap_response
    
    def ascii_response(self):
        opendap_response = self.get_opendap_response()
        return opendap_response     
        
    def file_response(self):
        opendap_response = self.get_opendap_response()
        return opendap_response     
    
    def html_response(self):
        opendap_response = self.get_opendap_response()
        html = opendap_response.text
        html = html.replace('document.forms[0]', 'document.forms[1]')
        html = html.replace(cherrypy.session['opendap_url'], local_host)
        return html

    def fetch_opendap_response(self):
        opendap_url = self.opendap_request_line()
        ret = requests.get(opendap_url)
        return ret

    def top_frame(self):
        form = """This is OCCUR. Currently using following OPeNDAP Server:
                        <form method="get">
                            <input type="text" size=40 value="{opendap_url}" name="opendap_url"/>
                            <button type="submit">launch</button>
                        </form>
                """.format(opendap_url=cherrypy.session['opendap_url'])
        return form

    def config(self):
        form = """
              <body>
                <form method="get">
                  <input type="text" size=40 value="http://opendap.jpl.nasa.gov:80/opendap" name="opendap_url"/>
                  <button type="submit">launch</button>
                </form>
              </body>
            """
        return form
    
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
