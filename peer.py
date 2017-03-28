from pyactor.context import set_context, create_host, sleep, serve_forever, interval
from pyactor.exceptions import TimeoutError


class Peer(object):
	_tell = ['announce_2_tracker', 'init_start', 'stop_interval', 'test', 'get_peers']
	_ask = ['push']
	_ref = []

    # Inicializador de la/as instancia/as del Peer
	def __init__(self):
		self.tracker = None
		self.torrent_hash = None
		self.interval1 = None
		self.interval2 = None
		self.keysList = {}
		self.chunk_id = None
		self.chunk_data = {}

	# Programamos los intervalos de announce y get_peers en 9 y 2 segundos respectivamente
	def init_start(self, tracker_proxy, torrent_hash):
		self.tracker = tracker_proxy
		self.torrent_hash = torrent_hash
		self.interval1 = interval(self.host, 9, self.proxy, 'announce_2_tracker')
		self.interval2 = interval(self.host, 2, self.proxy, 'get_peers')

	# Si tenemos el tracker y el torrent_hash, hacemos el announce
	def announce_2_tracker(self):
		if self.tracker and self.torrent_hash:
			tracker.announce(self.torrent_hash, str(self.proxy)[23:27])

	# Si tenemos el torrent_hash, hacemos el get_peers
	def get_peers(self):
		if self.torrent_hash:
			self.keysList = tracker.get_peers(self.torrent_hash)

	# Stop de los intervalos del announce y el get_peers
	def stop_interval(self):
		print "stopping interval"
		self.interval1.set()
		self.interval2.set()

	# Intentamos acceder al dato registrado en la posicion chunk_id, si lo tenemos lo devolvemos, si no, devolvemos None
	def push(self, chunk_id):
		self.chunk_id = chunk_id
		try:
			return self.chunk_data[self.chunk_id]
		except LookupError:
			return None

	# Comprovamos que mandamos solo el host
	def test(self):
		print self.proxy
		print str(self.proxy)[23:27]


if __name__ == "__main__":
    set_context()
    h = create_host('http://127.0.0.1:1679/')

    tracker = h.lookup_url('http://127.0.0.1:1277/tracker', 'Tracker', 'tracker')

    p1 = h.spawn('peer1', Peer)
    p1.init_start(tracker, 'hash_1')

    serve_forever()
