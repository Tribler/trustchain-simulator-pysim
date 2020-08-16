import logging
import random

from chainsim.peer import Peer
from chainsim.settings import NUM_PEERS, MAX_ROUNDS, RECORDS_PER_ROUND, CRAWL_BATCH
from ipv8.keyvault.crypto import ECCrypto

crypto = ECCrypto()
peers = []

lvl = logging.WARNING
logging.basicConfig(level=lvl)
logger = logging.getLogger(__name__)
logger.setLevel(lvl)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


def select_random_peer(selecting_peer):
    random_peer = random.choice(peers)
    while random_peer == selecting_peer:
        random_peer = random.choice(peers)
    return random_peer


def evaluate_round():
    for _ in range(RECORDS_PER_ROUND):
        for peer in peers:
            target_peer = select_random_peer(peer)
            latest_block = peer.database.get_latest(peer.public_key.key_to_bin())

            double_spend = False
            if random.random() <= 0.1 and not peer.did_double_spend and latest_block and latest_block.sequence_number > 1:
                peer.did_double_spend = True
                double_spend = True

            peer.record_interaction(target_peer, double_spend=double_spend)

    # let peers crawl
    for peer in peers:
        crawl_peer = select_random_peer(peer)
        start_seq = peer.database.get_lowest_sequence_number_unknown(crawl_peer.public_key.key_to_bin())
        end_seq = start_seq + CRAWL_BATCH
        crawl_peer.crawl(peer, start_seq, end_seq)


for peer_ind in range(1, NUM_PEERS + 1):
    keypair = crypto.generate_key("curve25519")
    peer = Peer(peer_ind, keypair)
    peers.append(peer)

for peer in peers:
    peer.set_peers(peers)


for round_num in range(1, MAX_ROUNDS + 1):
    evaluate_round()

    # Advance the round
    for peer in peers:
        peer.round = round_num

    # Count the number of exposed peers
    exposed = 0
    did_double_spend = 0
    for peer in peers:
        if peer.exposed != -1:
            exposed += 1
        if peer.did_double_spend:
            did_double_spend += 1

    logger.error("Evaluated round %d... (double spended: %d/%d, exposed: %d/%d)" % (
    round_num, did_double_spend, NUM_PEERS, exposed, NUM_PEERS))
