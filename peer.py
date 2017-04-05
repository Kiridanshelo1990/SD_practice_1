from pyactor.context import set_context, create_host, sleep, serve_forever, interval
from pyactor.exceptions import TimeoutError
import threading
import sys
import random


class Peer(object):
	_tell = ['announce_2_tracker', 'init_start', 'stop_interval', 'receive_push', 'get_peers', 'push', 'pull']
	_ask = ['send_pull']
	_ref = ['announce_2_tracker', 'get_peers', 'receive_push', 'push', 'pull', 'send_pull']

	# Inicializador de la/as instancia/as del Peer
	def __init__(self):
		# variable local a la instancia del peer que almacena el proxy del tracker
		self.tracker = None
		# variable local a la instancia del peer que almacena el torrent_hash (id del swarm en el tracker)
		self.torrent_hash = None
		# Intervalo que programa la ejecucion periodica del metodo 'announce_2_tracker'
		self.interval1 = None
		# Intervalo que programa la ejecucion periodica del metodo 'get_peers'
		self.interval2 = None
		# Intervalo que programa la ejecucion periodica del metodo 'push'
		self.interval3 = None
		# Lista que contendra los peers obtenidos mediante el metodo announce
		self.peer_list = []
		# Diccionario que contendra los pares clave-valor {chunk_id:chunk_data}
		self.chunk_dic = {}
		# Lista que contendra los ids de los chunks disponibles en el chunk_dic
		self.available_chunks_id = []
		# Lista que contendra los ids de los chunks no disponibles en el chunk_dic
		self.not_available_chunks_id = []
		# Lista que contiene los ids de cada chunk del torrent_hash
		self.id_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

	# Programamos los intervalos de announce y get_peers en 9 y 2 segundos respectivamente
	def init_start(self, tracker_proxy, torrent_hash, seeder):
		self.tracker = tracker_proxy
		self.torrent_hash = torrent_hash

		# Si el peer es el seeder inicializamos  las variables chunk_dic y available_chunks_id
		if seeder:
			id = 0
			for letter in 'HELLOWORLD':
				self.available_chunks_id.append(id)
				self.chunk_dic[id] = letter
				id += 1

		# Creamos una lista de los chunk_id que no tenemos
		for i in self.id_list:
			chunk_id = self.id_list[i]
			if chunk_id not in self.available_chunks_id:
				self.not_available_chunks_id.append(chunk_id)

		# Inicialzamos los intervalos
		self.interval1 = interval(self.host, 7, self.proxy, 'announce_2_tracker')
		self.interval2 = interval(self.host, 2, self.proxy, 'get_peers')
		#self.interval3 = interval(self.host, 1, self.proxy, 'push')
		self.interval4 = interval(self.host, 1, self.proxy, 'pull')

	# Metodo 'announce_2_tracker'
	# Realiza el announce del peer hacia el tracker
	def announce_2_tracker(self):
		if self.tracker and self.torrent_hash:
			tracker.announce(self.torrent_hash, self.proxy)

	# Metodo 'get_peers'
	# Solicita, al tracker, tuplas de peers aleatorios pertenecienetes al swarm
	def get_peers(self):
        # Si tenemos el torrent_hash realizamos el get_peers
		if self.torrent_hash:
			self.peer_list = tracker.get_peers(self.torrent_hash)

	# Metodo 'push'
	# Realiza la distribucion de chunks hacia otros peers
	def push(self):
		num_available_chunk = len(self.available_chunks_id)
		if num_available_chunk:
			for peer in self.peer_list:
				chunk_2_send = self.available_chunks_id[random.randrange(num_available_chunk)]
				peer.receive_push(chunk_2_send, self.chunk_dic[chunk_2_send])

	# Metodo 'receive_push'
	# soporta la distribucion de chunks procedentes de otros peers
	def receive_push(self, chunk_id, chunk_data):
		# Si no tenemos el chunk lo incorporamos
		if chunk_id not in self.available_chunks_id:
			self.available_chunks_id.append(chunk_id)
			self.chunk_dic[chunk_id] = chunk_data
		#elif True:
			 #---- Debug's lines ---
			#if len(self.available_chunks_id) == 10:
			    #print self.id + " has got all chunks!"
			    #print self.chunk_dic
			#else:
			    #print self.id + " has got " + str(len(self.available_chunks_id)) + " chunks"

	# Metodo 'pull'
	# Realiza la peticion de los chunk_data a otros peer de forma aleatoria mediante la tecnica pull
	def pull(self):
		num_not_available_chunk = len(self.not_available_chunks_id)
		if num_not_available_chunk:
			for peer in self.peer_list:
				if peer != self.proxy:
					try:
						chunk_2_pull = self.not_available_chunks_id[random.randrange(num_not_available_chunk)]
						chunk_data = peer.send_pull(chunk_2_pull, future=True)
						sleep (1)
						if chunk_data.done():
							if chunk_data.result() != None:
								self.available_chunks_id.append(chunk_2_pull)
								self.chunk_dic[chunk_2_pull] = chunk_data.result()
								self.not_available_chunks_id.remove(chunk_2_pull)
								print self.not_available_chunks_id
					except:
						pass
		else:
			self.interval4.set()

	# Metodo 'send_pull'
	# Retorna la chunk_data si esta disponible, si no, retorna None
	def send_pull(self, chunk_id):
		if chunk_id in self.available_chunks_id:
			return self.chunk_dic[chunk_id]
		else:
			return None

	# Stop de los intervalos del announce y el get_peers
	def stop_interval(self):
		print "stopping interval"
		self.interval1.set()
		self.interval2.set()

if __name__ == "__main__":
	if len(sys.argv) == 4:
		host_port = sys.argv[1]
		actor_id = sys.argv[2]
		hash = sys.argv[3]
		seeder = False
		if actor_id == 'peer0':
			seeder = True

		set_context()
		h = create_host('http://127.0.0.1:' + host_port + '/')

		tracker = h.lookup_url('http://127.0.0.1:1277/tracker', 'Tracker', 'tracker')
		p1 = h.spawn(actor_id, Peer)
		print actor_id + " spawned"
		p1.init_start(tracker, hash, seeder)
		serve_forever()
	else:
		print 'Argument\'s number error to execute the peer'
