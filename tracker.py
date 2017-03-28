from pyactor.context import set_context, create_host, sleep, serve_forever, interval
from pyactor.exceptions import TimeoutError


class Tracker(object):
    _tell = ['announce', 'init_start', 'check_peers']
    _ask = ['get_peers']
    _ref = ['announce']
    
    # Inicializador de la instancia del Tracker
    def __init__(self):
        self.swarmList = {}
        self.ttl = 10
        self.interval1 = None

    def init_start(self):
        # Programamos el intervalo que comprobara el ttl de los peer's
        # cada segundo
        self.interval1 = interval(self.host, 1, self.proxy, 'check_peers')


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

    # Funcion que s'encarga de comprobar el ttl de los peers
    # y eliminar de cada swarm aquellos que no estan activos
    def check_peers(self):
        for swarm in self.swarmList:
            if bool(self.swarmList[swarm]):
                for peer in self.swarmList[swarm]:
                    # Restamos el ttl una unidad
                    self.swarmList[swarm][peer] -= 1
                    if self.swarmList[swarm][peer] == 0:
                        del self.swarmList[swarm][peer]
                #print swarm
            else:
                # si el swarm no tiene peers lo eliminamos
                #print 'el swarm \'' + swarm + '\' esta vacio'
                del self.swarmList[swarm]


if __name__ == "__main__":
    # Inicializacion del contexto de la ejecucion del host
    # Por defecto el tipo de threads son los threads clasicos de python
    set_context()

    # Creacion del host que engendra el tracker
    host = create_host('http://127.0.0.1:1277/')

    # Generacion del 'tracker'
    tracker = host.spawn('tracker', Tracker)

    tracker.init_start()
    #print tck

    #print tck.get_peers('hash1')

    #p1 = h.spawn('peer1', Peer)
    #p1.send(tck)

    serve_forever()
