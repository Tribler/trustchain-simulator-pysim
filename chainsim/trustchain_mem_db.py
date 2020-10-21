import csv
import random
import time
from binascii import hexlify

from ipv8.attestation.trustchain.block import TrustChainBlock


class TrustchainMemoryDatabase(object):
    """
    This class defines an optimized memory database for TrustChain.
    """

    def __init__(self, env):
        self.block_cache = {}
        self.linked_block_cache = {}
        self.block_types = {}
        self.latest_blocks = {}
        self.original_db = None
        self.block_time = {}
        self.block_file = None
        self.kill_callback = None
        self.double_spends = []
        self.blocks = []
        self.hash_map = {}
        self.env = env

    def get_block_class(self, block_type):
        """
        Get the block class for a specific block type.
        """
        if block_type not in self.block_types:
            return TrustChainBlock

        return self.block_types[block_type]

    def add_block(self, block):
        self.block_cache[(block.public_key, block.sequence_number)] = block
        self.linked_block_cache[(block.link_public_key, block.link_sequence_number)] = block

        if block.public_key not in self.latest_blocks:
            self.latest_blocks[block.public_key] = block
        elif self.latest_blocks[block.public_key].sequence_number < block.sequence_number:
            self.latest_blocks[block.public_key] = block

        self.block_time[(block.public_key, block.sequence_number)] = int(round(time.time() * 1000))
        self.blocks.append(block)

    def get_random_blocks(self, num_random_blocks):
        return random.sample(self.blocks, min(len(self.blocks), num_random_blocks))

    def remove_block(self, block):
        if self.latest_blocks[block.public_key] == block:
            prev_block = self.get_block_before(block)
            if prev_block:
                self.latest_blocks[block.public_key] = prev_block
            else:
                self.latest_blocks.pop(block.public_key)

        self.block_cache.pop((block.public_key, block.sequence_number), None)
        self.linked_block_cache.pop((block.link_public_key, block.link_sequence_number), None)

    def get(self, public_key, sequence_number):
        if (public_key, sequence_number) in self.block_cache:
            return self.block_cache[(public_key, sequence_number)]
        return None

    def get_all_blocks(self):
        return self.block_cache.values()

    def get_number_of_known_blocks(self, public_key=None):
        if public_key:
            return len([pk for pk, _ in self.block_cache.keys() if pk == public_key])
        return len(self.block_cache.keys())

    def contains(self, block):
        return (block.public_key, block.sequence_number) in self.block_cache

    def get_latest(self, public_key, block_type=None):
        # TODO for now we assume block_type is None
        if public_key in self.latest_blocks:
            return self.latest_blocks[public_key]
        return None

    def get_latest_blocks(self, public_key, limit=25, block_types=None):
        latest_block = self.get_latest(public_key)
        if not latest_block:
            return []  # We have no latest blocks

        blocks = [latest_block]
        cur_seq = latest_block.sequence_number - 1
        while cur_seq > 0:
            cur_block = self.get(public_key, cur_seq)
            if cur_block and (not block_types or cur_block.type in block_types):
                blocks.append(cur_block)
                if len(blocks) >= limit:
                    return blocks
            cur_seq -= 1

        return blocks

    def get_block_after(self, block, block_type=None):
        # TODO for now we assume block_type is None
        if (block.public_key, block.sequence_number + 1) in self.block_cache:
            return self.block_cache[(block.public_key, block.sequence_number + 1)]
        return None

    def get_block_before(self, block, block_type=None):
        # TODO for now we assume block_type is None
        if (block.public_key, block.sequence_number - 1) in self.block_cache:
            return self.block_cache[(block.public_key, block.sequence_number - 1)]
        return None

    def get_lowest_sequence_number_unknown(self, public_key):
        if public_key not in self.latest_blocks:
            return 1
        latest_seq_num = self.latest_blocks[public_key].sequence_number
        for ind in range(1, latest_seq_num + 2):
            if (public_key, ind) not in self.block_cache:
                return ind

    def get_lowest_range_unknown(self, public_key):
        lowest_unknown = self.get_lowest_sequence_number_unknown(public_key)
        known_block_nums = [seq_num for pk, seq_num in self.block_cache.keys() if pk == public_key]
        filtered_block_nums = [seq_num for seq_num in known_block_nums if seq_num > lowest_unknown]
        if filtered_block_nums:
            return lowest_unknown, filtered_block_nums[0] - 1
        else:
            return lowest_unknown, lowest_unknown

    def get_linked(self, block):
        if (block.link_public_key, block.link_sequence_number) in self.block_cache:
            return self.block_cache[(block.link_public_key, block.link_sequence_number)]
        if (block.public_key, block.sequence_number) in self.linked_block_cache:
            return self.linked_block_cache[(block.public_key, block.sequence_number)]
        return None

    def get_linked_sq_pk(self, public_key, sequence_number):
        if (public_key, sequence_number) in self.linked_block_cache:
            return self.linked_block_cache[(public_key, sequence_number)]
        return None

    def crawl(self, public_key, start_seq_num, end_seq_num, limit=100):
        # TODO we assume only ourselves are crawled
        blocks = []
        orig_blocks_added = 0
        for seq_num in range(start_seq_num, end_seq_num + 1):
            if (public_key, seq_num) in self.block_cache:
                block = self.block_cache[(public_key, seq_num)]
                blocks.append(block)
                orig_blocks_added += 1
                linked_block = self.get_linked(block)
                if linked_block:
                    blocks.append(linked_block)

            if orig_blocks_added >= limit:
                break

        return blocks

    def commit_block_times(self):
        # self.write_work_graph()

        if self.block_file:
            with open(self.block_file, "a") as t_file:
                writer = csv.DictWriter(t_file, ['time', 'transaction', 'type', "seq_num", "link", 'from_id', 'to_id'])
                block_ids = list(self.block_time.keys())
                for block_id in block_ids:
                    block = self.block_cache[block_id]
                    time = self.block_time[block_id]
                    from_id = hexlify(block.public_key).decode()[-8:]
                    to_id = hexlify(block.link_public_key).decode()[-8:]
                    writer.writerow({"time": time, 'transaction': str(block.transaction),
                                     'type': block.type.decode(),
                                     'seq_num': block.sequence_number, "link": block.link_sequence_number,
                                     'from_id': from_id, 'to_id': to_id
                                     })
                    self.block_time.pop(block_id)

    def commit(self, my_pub_key):
        """
        Commit all information to the original database.
        """
        if self.original_db:
            my_blocks = [block for block in self.block_cache.values() if block.public_key == my_pub_key]
            for block in my_blocks:
                self.original_db.add_block(block)

    def add_double_spend(self, blk1, blk2):
        self.double_spends.append((blk1, blk2))

    def get_missing_blocks(self, public_key, latest_seq_num, num_missing):
        """
        Return missing blocks.
        """
        missing = []
        for seq_num in range(1, latest_seq_num):
            blk = self.get(public_key, seq_num)
            if not blk:
                missing.append(seq_num)

        return random.sample(missing, min(num_missing, len(missing)))

    def close(self):
        if self.original_db:
            self.original_db.close()
