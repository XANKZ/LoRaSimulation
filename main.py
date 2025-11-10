from Node import Node
from Gateway import Gateway
from Channel import calculate_rssi
import random

print("Bắt đầu chương trình mô phỏng.")

number_of_nodes = 5
nodes = []

for i in range(number_of_nodes):
    random_x = random.randint(0,10000)
    random_y = random.randint(0,10000)

    new_node = Node(node_id = i, x = random_x, y = random_y)
    nodes.append(new_node)

gateways = []
gateways.append( Gateway(gateway_id=0, x = random.randint(0,10000), y = random.randint(0,10000)) )

print("\nĐã khởi tạo xong Node. Bắt đầu vòng lặp thời gian...")

stimulation_duration_seconds = 1200
for time_step in range(stimulation_duration_seconds):
    for node in nodes:
        packet = node.update(time_step)

        if packet:
            print(f"!!! Thời gian {time_step}s: Node {Node.id} đang phát gói tin.")

            for gw in gateways:
                rssi = calculate_rssi(node,gw)
                gw.receive_packet(packet,rssi)

print("\nKết thúc mô phỏng.")