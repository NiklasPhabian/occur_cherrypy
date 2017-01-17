import requests
import cherrypy
from makoLoader import MakoLoader
main = MakoLoader()
cherrypy.tools.mako = cherrypy.Tool('on_start_resource', main)


class Occur:
    exposed = True

    def GET(self, *args, **kwargs):
        return self.test2()

    @cherrypy.tools.mako(filename="index.html")
    def test(self):
        ret = requests.get('http://opendap.jpl.nasa.gov:80/')
        return {'top_msg': 'top', 'main_msg': ret.text}

    def test2(self):

        ret = requests.get('http://opendap.jpl.nasa.gov:80/opendap')
        return ret

if __name__ == '__main__':
    conf = {'/': {
        'tools.sessions.on': True,
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.staticfile.filename': '/css/frame.css',
        'tools.mako.collection_size': 500,
        'tools.mako.directories': 'templates/',
        'tools.encode.on': True}
    }
    cherrypy.tree.mount(Occur(), '/opendap', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
