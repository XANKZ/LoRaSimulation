import random

# Năng lượng có thể là micro-joule
ENERGY_CONSUMPTION = {
    "SENSE": 50,        # Năng lượng tiêu hao trong lúc đo
    "TRANSMIT": 500,    # Năng lượng truyền tin
    "SLEEP_TICK":1      # Năng lượng tiêu hao khi ngủ
}

TEMPERATURE_TRANSMIT_THRESHOLD = 0.5    # Ngưỡng thay đổi nhiệt độ để gửi tin 1 
AIR_HUMIDITY_TRANSMIT_THRESHOLD = 2         # Ngưỡng thay đổi độ ẩm đất để truyền tin 2%
SOIL_MOISURE_TRANSMIT_THRESHOLD = 3      # Ngưỡng thay đổi độ ẩm đất để truyền tin 3%
# Hằng số của mạng LoRa
# Giả sử băng thông 125kHz, Coding Rate 4/5, Payload 10 bytes
TIME_ON_AIR = {
    7: 0.03,    # SF7: ~30ms
    8: 0.05,    # SF8: ~50ms
    9: 0.09,    # SF9: ~90ms
    10: 0.16,   # SF10: ~160ms
    11: 0.33,   # SF11: ~330ms
    12: 0.58    # SF12: ~580ms
}

HEARTBEAT_INTERVAL = 4 * 3600

class  Node:
    def __init__(self, node_id, x, y, sf):
        print(f">>> Khởi tạo vị trí node tại vị trí ({x},{y}).")
        self.id = node_id
        self.pos = (x,y)
        self.sf = sf #Spreading factor của node
        self.channel = 0 # Giả sử tất cả các node dùng chung 1 kênh
        self.state = "SLEEP"
        self.next_wake_up_time = random.uniform(0,60)
        self.energy_level = 100000.0
        self.last_sent_temperature = None
        self.last_sent_air_humidity = None
        self.last_sent_soil_moisure = None
        self.laste_heartbeat_time = 0
    
    def go_to_sleep(self, current_time, sleep_duration):
        self.state = "SLEEP"

        jitter = random.uniform(-2.0 , 2.0)
        actual_sleep_duration = sleep_duration + jitter

        self.next_wake_up_time = current_time + actual_sleep_duration
        print(f">>> Hiện tại {current_time}s: Nodes{self.id} đi ngủ. Thức dậy vào lúc {self.next_wake_up_time}s.")

    def create_packet(self):
        self.energy_level -= ENERGY_CONSUMPTION["SENSE"]
        print(f"    Node {self.id} [Đo đạc]. Năng lượng còn lại: {self.energy_level:.2f}")

        temperature = 0 + 50 * random.random()
        air_humidity = 0 + 100 * random.random()
        soil_moisure = 0 + 60 * random.random()
        packet = {
            'source_id': self.id,
            'data': (temperature, air_humidity, soil_moisure),
            'sf': self.sf,
            'channel': self.channel
        }
        #print(f"    Node {self.id} đã tạo gói tin với NHIỆT ĐỘ: {temperature:.2f}'C và ĐỘ ẨM KHÔNG KHÍ: {humidity:.2f}%RH và ĐỘ ẨM ĐẤT: {soil_moisure:.2f}.")
        return packet
    
    def transmit_packet(self, packet):
        self.energy_level -= ENERGY_CONSUMPTION["TRANSMIT"]
        temperature, air_humidity, soil_moisure = packet['data']
        print(f"    Node {self.id} đã tạo gói tin với NHIỆT ĐỘ: {temperature:.2f}'C và ĐỘ ẨM KHÔNG KHÍ: {air_humidity:.2f}%RH và ĐỘ ẨM ĐẤT: {soil_moisure:.2f}%.")
        print(f"    Node {self.id} [Truyền tin]. Năng lượng còn lại: {self.energy_level:.2f}")
        return packet

    def update(self, current_time):
        logs = []

        if self.energy_level <= 0:
            if self.state != "DEAD":
                print(f">>> Node {self.id} đã cạn kiệt năng lượng và ngừng hoạt động.")
                self.state = "DEAD"
            return None, logs

        packet_to_send = None

        if self.state == "SLEEP":
            self.energy_level -= ENERGY_CONSUMPTION["SLEEP_TICK"]

        if self.state == "SLEEP" and current_time >= self.next_wake_up_time:
            self.state = "SENSING"
            logs.append({'event': 'WAKE_UP', 'details': ''})
            print(f">>> Thời gian hiện tại {current_time}s: Node{self.id} thức dậy để đo dữ liệu.")
            sensing_time = 5

            # Đo và tạo gói tin
            packet = self.create_packet()
            current_temperature, current_air_humidity, current_soil_moisure = packet['data']

            # Logic
            should_transmit = False
            reason_to_transmit = ""

            # Lần đầu
            if (self.last_sent_temperature is None
                and self.last_sent_air_humidity is None
                and self.last_sent_soil_moisure is None):
                should_transmit = True
                reason_to_transmit = "Gửi lần đầu."

            else:
                temperature_change = abs(current_temperature - self.last_sent_temperature)
                air_humidiy_change = abs(current_air_humidity - self.last_sent_air_humidity)
                soil_moisure_change = abs(current_soil_moisure - self.last_sent_soil_moisure)

                if temperature_change > TEMPERATURE_TRANSMIT_THRESHOLD:
                    should_transmit = True
                    reason_to_transmit = f"Nhiệt độ thay đổi lớn ({temperature_change:.2f}'C)"
                elif air_humidiy_change > AIR_HUMIDITY_TRANSMIT_THRESHOLD:
                    should_transmit = True
                    reason_to_transmit = f"Độ ẩm không khí thay đổi lớn ({air_humidiy_change:.2f}%)"
                elif soil_moisure_change > SOIL_MOISURE_TRANSMIT_THRESHOLD:
                    should_transmit = True
                    reason_to_transmit = f"Độ ẩm đất thay đổi lớn ({soil_moisure_change:.2f}%)"

            time_since_last_heartbeat = current_time - self.laste_heartbeat_time
            if not should_transmit and time_since_last_heartbeat > HEARTBEAT_INTERVAL:
                should_transmit = True
                reason_to_transmit = "Gửi tin Heartbeat định kỳ."

            logs.append(
                {
                    'event': 'DECISION',
                    'details': reason_to_transmit or "Thay đổi không đáng kể."
                }
            )
            if should_transmit:
                print(f"    Node {self.id}: Quyết định gửi gói tin đi với lý do: {reason_to_transmit}")
            # Truyền gói tin
                packet_to_send = self.transmit_packet(packet)
                self.last_sent_temperature = current_temperature
                self.last_sent_air_humidity = current_air_humidity
                self.last_sent_soil_moisure = current_soil_moisure
            else:
                print(f"    Node {self.id}: Các giá trị thay đổi không đáng kể. Không gửi tin.")
            # Đi ngủ
            print(f">>> Thời gian hiện tại {current_time}s: Node {self.id} đi ngủ trong 30s")
            self.go_to_sleep(current_time + sensing_time, 30)
        return packet_to_send, logs
    
    def update_and_get_log(self, current_time):
        logs = []
        prev_state = self.state
        packet, internal_logs = self.update(current_time)

        logs.extend(internal_logs)

        # nếu node chết
        if self.state == "DEAD" and prev_state != "DEAD":
            logs.append({'event': 'DEAD', 'details': 'Node đã cạn năng lượng và ngưng hoạt động.'})

        if packet:
            # packet['data'] là tuple (temp, hum, soil)
            logs.append({'event': 'SENSE', 'details': f"Đo được {packet['data']}"})
            logs.append({'event': 'TX', 'details': f"Truyền trên kênh {packet.get('channel')} SF{packet.get('sf')}"})

        return {'packet': packet, 'logs': logs}
