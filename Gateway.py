class Gateway:
    def __init__(self, gateway_id, x,y):
        print(f" Khởi tạo Gateway {gateway_id} tại vị trí ({x},{y})")
        self.id = gateway_id
        self.pos = (x, y)
        self.sensitivity = -120.0
    
    def receive_packet(self, packet, rssi):
        if rssi >= self.sensitivity:
            print(f"    >>> Gateway {self.id} đã NHẬN được gói dữ liệu từ Node {packet['source_id']} với tín hiệu RSSI = {rssi:.2f} dBm" )
            return True
        else:
            print(f"    --- Gateway {self.id} KHÔNG nhận được gói tín từ Node {packet['source_id']} ví tín hiệu quá yếu: RSSI = {rssi:.2f} dBm")
            return False