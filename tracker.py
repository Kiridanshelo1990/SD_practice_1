from pyactor.context import set_context, create_host, sleep, serve_forever
from pyactor.exceptions import TimeoutError


class Tracker(object):
    _tell = ['announce', 'test', 'get_swarms']
    _ask = ['get_peers']
    _ref = ['announce']
    
    # Inicializador de la instancia del Tracker
    def __init__(self):
        self.swarmList = {}
        self.ttl = 10

    def test(self, msg):
        print msg

    # Funcion 'announce' del Tracker
    def announce(self, torrent_hash, peer_ref):
        # Comprobamos si existe el swarm del torrent_hash
        if torrent_hash in self.swarmList:
            # Comprobamos si el peer existe en el swarm
            if peer_ref in self.swarmList[torrent_hash]:
                # Si existe le restauramos el ttl
                self.swarmList[torrent_hash][peer_ref] = self.ttl

                print 'Announce from: ' + peer_ref # -----DEBUGGING LINE-----
            else:
                self.swarmList[torrent_hash][peer_ref] = self.ttl
        else:
            # Sino existe el swarm lo creamos y incorporamos el peer
            self.swarmList[torrent_hash] = {peer_ref: self.ttl}
            #print self.swarmList


    # Funcion 'get_peers'
    def get_peers(self, torrent_hash):
        if torrent_hash in self.swarmList:
            return self.swarmList[torrent_hash].keys()

    def check_peers(selfself):
        pass

    def get_swarms(self):
        print self.swarmList


class Peer(object):
    _tell = ['send']
    _ask = []

    def send(self, trck):
        trck.test('Hola desde peer')

if __name__ == "__main__":
    # Inicializacion del contexto de la ejecucion del host
    # Por defecto el tipo de threads son los threads clasicos de python
    set_context()

    # Creacion del host que engendra el tracker
    h = create_host('http://127.0.0.1:1277/')

    # Generacion del 'tracker'
    tck = h.spawn('tracker', Tracker)
    #print tck

    #print tck.get_peers('hash1')

    #p1 = h.spawn('peer1', Peer)
    #p1.send(tck)

    serve_forever()
