import logging
import random

from chainsim.settings import FANOUT, SHARE_INCONSISTENCIES
from chainsim.trustchain_mem_db import TrustchainMemoryDatabase

from ipv8.attestation.trustchain.block import TrustChainBlock, ValidationResult, UNKNOWN_SEQ, GENESIS_SEQ


class Peer(object):

    def __init__(self, id, key):
        self.id = id
        self.database = TrustchainMemoryDatabase()
        self.key = key
        self.public_key = self.key.pub()
        self.peers = None
        self.peers_lk = {}
        self.did_double_spend = False
        self.exposed = -1
        self.round = 1
        self.logger = logging.getLogger(__name__)

    def set_peers(self, peers):
        self.peers = peers
        for peer in self.peers:
            self.peers_lk[peer.public_key.key_to_bin()] = peer

    def get_peer_with_pk(self, public_key):
        return self.peers_lk.get(public_key, None)

    def record_interaction(self, target_peer, double_spend=False):
        block = TrustChainBlock.create(b'transfer',
                                       {},
                                       self.database,
                                       self.public_key.key_to_bin(),
                                       link_pk=target_peer.public_key.key_to_bin(),
                                       double_spend=double_spend)
        block.sign(self.key)

        if double_spend:
            self.logger.warning("[Peer %d] Double spending with peer %d (height: %d)!", self.id, target_peer.id, block.sequence_number)

        if not self.database.contains(block):
            self.database.add_block(block)

        # Make sure the counterparty confirms the block
        target_peer.process_incoming_block(self, block)

        # Broadcast the block to random peers
        if not double_spend:
            self.broadcast_block(block)

    def process_incoming_block(self, from_peer, block, should_share=True):
        self.logger.debug("[Peer %d] Received block (%d, %d) from peer %d", self.id, self.get_peer_with_pk(block.public_key).id, block.sequence_number, from_peer.id)
        validation = block.validate(self.database)

        if validation.did_double_spend:
            # We exposed the peer that created the incoming block!
            exposed_peer = self.get_peer_with_pk(block.public_key)
            if exposed_peer:
                self.logger.info("[Peer %d] exposed peer %d!", self.id, exposed_peer.id)
                exposed_peer.exposed = self.round

        if validation.is_inconsistent and SHARE_INCONSISTENCIES and should_share and validation.state == ValidationResult.valid:
            self.broadcast_inconsistencies(validation.inconsistent_blocks)

        if validation.state == ValidationResult.invalid:
            pass
        elif not self.database.contains(block):
            self.database.add_block(block)

        # Is this a request addressed at us?
        if (block.link_sequence_number != UNKNOWN_SEQ
                or block.link_public_key != self.public_key.key_to_bin()
                or self.database.get_linked(block) is not None):
            return

        # Counter-sign the block
        comfirm_block = TrustChainBlock.create(block.type,
                                               None,
                                               self.database,
                                               self.public_key.key_to_bin(),
                                               link=block)
        comfirm_block.sign(self.key)

        if not self.database.contains(comfirm_block):
            self.database.add_block(comfirm_block)

        # Send the block back
        from_peer.process_incoming_block(self, comfirm_block)

        # Broadcast the block pair
        self.broadcast_block_pair(block, comfirm_block)

    def crawl(self, from_peer, start_seq_num, end_seq_num):
        # It could be that our start_seq_num and end_seq_num are negative. If so, convert them to positive numbers,
        # based on the last block of ones chain.
        if start_seq_num < 0:
            last_block = self.database.get_latest(self.public_key.key_to_bin())
            start_seq_num = max(GENESIS_SEQ, last_block.sequence_number + start_seq_num + 1) \
                if last_block else GENESIS_SEQ
        if end_seq_num < 0:
            last_block = self.database.get_latest(self.public_key.key_to_bin())
            end_seq_num = max(GENESIS_SEQ, last_block.sequence_number + end_seq_num + 1) \
                if last_block else GENESIS_SEQ

        blocks = self.database.crawl(self.public_key.key_to_bin(), start_seq_num, end_seq_num, limit=10)
        # if self.settings.crawl_send_random_blocks > 0:
        #     random_blocks = self.persistence.get_random_blocks(self.settings.crawl_send_random_blocks)
        #     if random_blocks:
        #         blocks.extend(random_blocks)

        for block in blocks:
            from_peer.process_incoming_block(self, block)

    def broadcast_block(self, block):
        for peer in random.sample(self.peers, min(len(self.peers), FANOUT)):
            peer.process_incoming_block(self, block)

    def broadcast_inconsistencies(self, blocks):
        for peer in random.sample(self.peers, min(len(self.peers), FANOUT)):
            for block in blocks:
                peer.process_incoming_block(self, block, should_share=False)

    def broadcast_block_pair(self, block1, block2):
        for peer in random.sample(self.peers, min(len(self.peers), FANOUT)):
            peer.process_incoming_block(self, block1)
            peer.process_incoming_block(self, block2)
