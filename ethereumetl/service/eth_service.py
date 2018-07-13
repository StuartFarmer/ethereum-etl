class EthService(object):
    def __init__(self, web3):
        self._web3 = web3

    def get_block_range_for_timestamps(self, start_timestamp, end_timestamp):
        if start_timestamp > end_timestamp:
            raise ValueError('start_timestamp must be greater or equal to end_timestamp')

        try:
            start_block_bounds = self.get_block_number_bounds_for_timestamp(start_timestamp)
        except OutOfBounds:
            start_block_bounds = (0, 0)

        end_block_bounds = self.get_block_number_bounds_for_timestamp(end_timestamp)

        if start_block_bounds == end_block_bounds and start_block_bounds[0] != start_block_bounds[1]:
            raise ValueError('The given timestamp range does not cover any blocks')

        start_block = start_block_bounds[1]
        end_block = end_block_bounds[0]

        if start_block == 1:
            start_block = 0

        return start_block, end_block

    def get_block_number_bounds_for_timestamp(self, timestamp):
        start_block = self._web3.eth.getBlock(1)
        end_block = self._web3.eth.getBlock('latest')

        result = self._get_block_number_bounds_for_timestamp_recursive(timestamp, start_block, end_block)
        return result

    def _get_block_number_bounds_for_timestamp_recursive(self, timestamp, start_block, end_block):
        start_number, end_number = start_block.number, end_block.number
        start_timestamp, end_timestamp = start_block.timestamp, end_block.timestamp

        if timestamp < start_timestamp or timestamp > end_timestamp:
            raise OutOfBounds('timestamp {} is out of bounds for blocks {}-{}, timestamps {}-{}'
                              .format(timestamp, start_number, end_number, start_timestamp, end_timestamp))

        if timestamp == start_timestamp:
            return start_number, start_number
        elif timestamp == end_timestamp:
            return end_number, end_number
        elif (end_number - start_number) <= 1:
            return start_number, end_number
        else:
            assert start_timestamp <= timestamp <= end_timestamp
            # Block numbers must increase strictly monotonically
            assert start_timestamp < end_timestamp

            # Uses dichotomy method, complexity log(n) where n is the number of blocks
            # TODO: Optimize it by using gradient decent
            middle_number = start_number + int((end_number - start_number) / 2)
            middle_block = self._web3.eth.getBlock(middle_number)
            middle_timestamp = middle_block.timestamp

            if middle_timestamp < timestamp:
                new_block_range = middle_block, end_block
            else:
                new_block_range = start_block, middle_block

            return self._get_block_number_bounds_for_timestamp_recursive(timestamp, *new_block_range)


class OutOfBounds(Exception):
    pass
