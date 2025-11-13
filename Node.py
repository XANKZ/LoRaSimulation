import random

# Năng lượng có thể là micro-joule
ENERGY_CONSUMPTION = {
    "SENSE": 50,        # Năng lượng tiêu hao trong lúc đo
    "TRANSMIT": 500,    # Năng lượng truyền tin
    "SLEEP_TICK":1      # Năng lượng tiêu hao khi ngủ
}

TEMPERATURE_TRANSMIT_THRESHOLD = 0.5    # Ngưỡng thay đổi nhiệt độ để gửi tin 1 ĐỘ MIXI
HUMIDITY_TRANSMIT_THRESHOLD = 2         # Ngưỡng thay đổi độ ẩm đất để truyền tin 2%
SOIL_MOISURE_TRASMIT_THRESHOLD = 3      # Ngưỡng thay đổi độ ẩm đất để truyền tin 3%
# Còn 1 vấn để nếu các thông số để đo không thay đổi quá nhiều làm sao để gateway biết
# Là node hỏng hay nhiệt độ còn thay đổi ít

# Hằng số của mạng LoRa
TIME_ON_AIR = {
    7: 0.03,    # SF7: ~30ms
    8: 0.05,    # SF8: ~50ms
    9: 0.09,    # SF9: ~90ms
    10: 0.16,   # SF10: ~160ms
    11: 0.33,   # SF11: ~330ms
    12: 0.58    # SF12: ~580ms
}

class  Node:
    def __init__(self, node_id, x, y, sf):
        print(f">>> Khởi tạo vị trí node tại vị trí ({x},{y}).")
        self.id = node_id
        self.pos = (x,y)
        self.sf = sf #Spreading factor của node
        self.channel = 0 # Giả sử tất cả các node dùng chung 1 kênh
        self.state = "SLEEP"
        self.next_wake_up_time = 0
        self.energy_level = 100000.0
        self.last_sent_temperature = None
        self.last_sent_humidity = None
        self.last_sent_soil_moisure = None
    
    def go_to_sleep(self, current_time, sleep_duration):
        self.state = "SLEEP"
        self.next_wake_up_time = current_time + sleep_duration
        print(f">>> Hiện tại {current_time}s: Nodes{self.id} đi ngủ. Thức dậy vào lúc {self.next_wake_up_time}s.")

    def create_packet(self):
        self.energy_level -= ENERGY_CONSUMPTION["SENSE"]
        print(f"    Node {self.id} [Đo đạc]. Năng lượng còn lại: {self.energy_level:.2f}")

        temperature = 0 + 50 * random.random()
        humidity = 0 + 100 * random.random()
        soil_moisure = 0 + 60 * random.random()
        packet = {
            'source_id': self.id,
            'data': (temperature, humidity, soil_moisure),
            'sf': self.sf,
            'channel': self.channel
        }
        #print(f"    Node {self.id} đã tạo gói tin với NHIỆT ĐỘ: {temperature:.2f}'C và ĐỘ ẨM KHÔNG KHÍ: {humidity:.2f}%RH và ĐỘ ẨM ĐẤT: {soil_moisure:.2f}.")
        return packet
    
    def transmit_packet(self, packet):
        self.energy_level -= ENERGY_CONSUMPTION["TRANSMIT"]
        temperature, humidity, soil_moisure = packet['data']
        print(f"    Node {self.id} đã tạo gói tin với NHIỆT ĐỘ: {temperature:.2f}'C và ĐỘ ẨM KHÔNG KHÍ: {humidity:.2f}%RH và ĐỘ ẨM ĐẤT: {soil_moisure:.2f}.")
        print(f"    Node {self.id} [Truyền tin]. Năng lượng còn lại: {self.energy_level:.2f}")
        return packet

    def update(self, current_time):
        if self.energy_level <= 0:
            if self.state != "DEAD":
                print(f">>> Node {self.id} đã cạn kiệt năng lượng và ngừng hoạt động.")
                self.state = "DEAD"
            return None

        packet_to_send = None

        if self.state == "SLEEP":
            self.energy_level -= ENERGY_CONSUMPTION["SLEEP_TICK"]

        if self.state == "SLEEP" and current_time >= self.next_wake_up_time:
            self.state = "SENSING"
            print(f">>> Thời gian hiện tại {current_time}s: Node{self.id} thức dậy để đo dữ liệu.")
            sensing_time = 5

            # Đo và tạo gói tin
            packet = self.create_packet()
            current_temperature, current_humidity, current_soil_moisure = packet['data']

            # Logic
            should_transmit = False
            # Lần đầu
            if (self.last_sent_temperature is None
                and self.last_sent_humidity is None
                and self.last_sent_soil_moisure is None):
                should_transmit = True
            else:
                change = abs(current_temperature - self.last_sent_temperature)
                if change > TEMPERATURE_TRANSMIT_THRESHOLD:
                    print(f"    Node {self.id} phát hiện thay đổi lớn ({change:.2f}'C). Sẽ gửi tin đi.")
                    should_transmit = True
                else:
                    print(f"    Node {self.id}: Thay đổi không đáng kể ({change:.2f}'C). Không gửi tin.")

            if should_transmit:
            # Truyền gói tin
                packet_to_send = self.transmit_packet(packet)
                self.last_sent_temperature = current_temperature
                self.last_sent_humidity = current_humidity
                self.last_sent_soil_moisure = current_soil_moisure
            # Đi ngủ
                print(f">>> Thời gian hiện tại {current_time}s: Node {self.id} đi ngủ trong 60s")
                self.go_to_sleep(current_time + sensing_time, 30)
        return packet_to_send
    