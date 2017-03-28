from pyactor.context import set_context, create_host, sleep, serve_forever, interval
from pyactor.exceptions import TimeoutError


class Peer(object):
    _tell = ['announce_2_tracker', 'init_start', 'stop_interval', 'test']
    _ask = ['peer_prog']
    _ref = []

    # Inicializador de la/as instancia/as del Peer
    def __init__(self):
        self.tracker = None
        self.torrent_hash = None
        self.interval1 = None

    def init_start(self, tracker_proxy, torrent_hash):
        self.tracker = tracker_proxy
        self.torrent_hash = torrent_hash
        self.interval1 = interval(self.host, 4, self.proxy, 'announce_2_tracker')

    def announce_2_tracker(self):
        if self.tracker and self.torrent_hash:
            tracker.announce(self.torrent_hash, str(self.proxy))

    def stop_interval(self):
        print "stopping interval"
        self.interval1.set()

    def test(self):
        print self.proxy


if __name__ == "__main__":
    set_context()
    h = create_host('http://127.0.0.1:1679/')

    tracker = h.lookup_url('http://127.0.0.1:1277/tracker', 'Tracker', 'tracker')

    p1 = h.spawn('peer1', Peer)
    p1.init_start(tracker, 'hash_1')

    serve_forever()
