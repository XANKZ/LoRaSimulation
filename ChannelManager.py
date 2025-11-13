TIME_ON_AIR = {
    7: 0.03,    # SF7: ~30ms
    8: 0.05,    # SF8: ~50ms
    9: 0.09,    # SF9: ~90ms
    10: 0.16,   # SF10: ~160ms
    11: 0.33,   # SF11: ~330ms
    12: 0.58    # SF12: ~580ms
}

class ChannelManager:
    def __init__(self, num_channels = 1):
        # channels là một dictionary, key là số hiệu kênh (0, 1, 2...)
        # value là một dictionary khác cho từng SF
        # Ví dụ: self.channels[0][7] sẽ lưu thời điểm kênh 0/SF7 rảnh.
        self.channels = {}
        for i in range(num_channels):
            self.channels[i] = {
                7: 0.03,    # SF7: ~30ms
                8: 0.05,    # SF8: ~50ms
                9: 0.09,    # SF9: ~90ms
                10: 0.16,   # SF10: ~160ms
                11: 0.33,   # SF11: ~330ms
                12: 0.58    # SF12: ~580ms
            }
    
    def check_collision(self, packet, current_time):
        channel_id = packet['channel']
        sf = packet['sf']
        free_time = self.channels[channel_id][sf]

        if current_time < free_time:
            print(f"    XXX XUNG ĐỘT trên kênh {channel_id}/SF{sf}! Gói tin từ Node {packet['source_id']} đã bị mất.")
            return True
        else:
            toa = TIME_ON_AIR[sf]
            self.channels[channel_id][sf] = current_time + toa
            return False