import random

class  Node:
    def __init__(self, node_id, x, y):
        print(f">>> Khởi tạo vị trí node tại vị trí ({x},{y}).")
        self.id = node_id
        self.pos = (x,y)
        self.state = "SLEEP"
        self.next_wake_up_time = 0
    
    def go_to_sleep(self, current_time, sleep_duration):
        self.state = "SLEEP"
        self.next_wake_up_time = current_time + sleep_duration
        print(f">>> Hiện tại {current_time}s: Nodes{self.id} đi ngủ. Thức dậy vào lúc {self.next_wake_up_time}s.")

    def create_packet(self):
        temperature = 0 + 50 * random.random()
        humidity = 0 + 100 * random.random()
        packet = {
            'source_id': self.id,
            'data': (temperature, humidity)
        }
        print(f"    Node {self.id} đã tạo gói tin với NHIỆT ĐỘ: {temperature:.2f}'C và ĐỘ ẨM: {humidity:.2f}%.")
        return packet
    
    def update(self, current_time):
        packet_to_send = None
        if self.state == "SLEEP" and current_time >= self.next_wake_up_time:
            self.state = "SENSING"
            print(f">>> Thời gian hiện tại {current_time}s: Node{self.id} thức dậy để đo dữ liệu.")
            sensing_time = 5
            packet_to_send = self.create_packet()
            self.go_to_sleep(current_time + sensing_time, 60)

    