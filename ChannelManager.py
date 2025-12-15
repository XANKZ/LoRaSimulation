# Đang là binary collision giờ thêm capture effect và adr
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
        # self.channels = {}
        # for i in range(num_channels):
        #     self.channels[i] = {
        #         7: 0.03,    # SF7: ~30ms
        #         8: 0.05,    # SF8: ~50ms
        #         9: 0.09,    # SF9: ~90ms
        #         10: 0.16,   # SF10: ~160ms
        #         11: 0.33,   # SF11: ~330ms
        #         12: 0.58    # SF12: ~580ms
        #     }

        # Lưu trữ gói tin đang chiếm kênh: {channel_id: {sf: {'end_time': float, 'rssi': float, 'packet_id': int}}}
        self.active_transmissions = {}
        for i in range(num_channels):
            self.active_transmissions[i] = {}
    
    def check_collision(self, packet, current_time, packet_rssi):
        channel_id = packet['channel']
        sf = packet['sf']
        #free_time = self.channels[channel_id][sf]

        # if current_time < free_time:
        #     print(f"    XXX XUNG ĐỘT trên kênh {channel_id}/SF{sf}! Gói tin từ Node {packet['source_id']} đã bị mất.")
        #     return True
        # else:
        #     toa = TIME_ON_AIR[sf]
        #     self.channels[channel_id][sf] = current_time + toa
        #     return False

        if sf in self.active_transmissions[channel_id]:
            if self.active_transmissions[channel_id][sf]['end_time'] < current_time:
                del self.active_transmissions[channel_id][sf]
        
        if sf in self.active_transmissions[channel_id]:
            existing = self.active_transmissions[channel_id][sf]

            CAPTURE_THRESHOLD = 6

            if packet_rssi > (existing['rssi'] + CAPTURE_THRESHOLD):
                 print(f"    [Capture] Gói từ Node {packet['source_id']} (-{abs(packet_rssi)}dBm) ĐÈ gói cũ (-{abs(existing['rssi'])}dBm).")

                 toa = TIME_ON_AIR[sf]
                 self.active_transmissions[channel_id][sf] = {
                     'end_time': current_time + toa,
                     'rssi': packet_rssi,
                     'source_id': packet['source_id']
                 }
                 return False
            else:
                # Gói mới yếu hơn hoặc ngang bằng -> Gói mới CHẾT
                print(f"    [Loss] Gói từ Node {packet['source_id']} bị mất do xung đột.")
                return True
        else:
            toa = TIME_ON_AIR[sf]
            self.active_transmissions[channel_id][sf] = {
                'end_time': current_time + toa,
                'rssi': packet_rssi,
                'source_id': packet['source_id']
            }
            return False