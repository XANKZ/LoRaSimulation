from Node import Node
from Gateway import Gateway
from Channel import calculate_rssi
from ChannelManager import ChannelManager
import random

print("Bắt đầu chương trình mô phỏng.")

number_of_nodes = 100
nodes = []

for i in range(number_of_nodes):
    random_x = random.randint(0,10000)
    random_y = random.randint(0,10000)

    assigned_sf = random.choice([7, 8, 9, 10, 11, 12])
    # Cái này thực tế được điều khiển bới ADR nhưng nếu có thuật toán thì cần sửa đổi

    new_node = Node(node_id = i, x = random_x, y = random_y, sf = assigned_sf)
    nodes.append(new_node)

gateways = []
gateways.append( Gateway(gateway_id=0, x = random.randint(0,10000), y = random.randint(0,10000)) )

channel_manager = ChannelManager(num_channels = 1)
# Cần nghiên cứu lại chỗ này, không biết chắc là LoRa có hoạt động như vậy không

print("\nĐã khởi tạo xong Node và Gateway. Bắt đầu vòng lặp thời gian...")

total_packets_sent = 0
total_packets_receive = 0
total_collision = 0

stimulation_duration_seconds = 86400
for time_step in range(stimulation_duration_seconds):
    if time_step %3600 == 0:
        print(f" Giờ thứ {time_step // 3600}.")
    for node in nodes:
        packet = node.update(time_step)

        if packet:
            total_packets_sent += 1

            is_collided = channel_manager.check_collision(packet, time_step)
            if is_collided:
                total_collision += 1
                continue
            print(f"!!! Thời gian {time_step}s: Node {node.id} đang phát gói tin.")

            is_receive_by_any_gw = False
            
            for gw in gateways:
                rssi = calculate_rssi(node, gw)
                if gw.receive_packet(packet, rssi):
                    is_receive_by_any_gw = True
                    break
            
            if is_receive_by_any_gw:
                total_packets_receive += 1

print("\nKết thúc mô phỏng.")
print(f" Tổng thời gian mô phỏng: {stimulation_duration_seconds / 3600:.1f} giờ.")
print(f" Tổng các gói tin đẫ nhận được bởi các node: {total_packets_sent}.")
print(f" Tổng các gói tin đã nhận bởi gateway: {total_packets_receive}.")

total_energy_left = 0
for node in nodes:
    total_energy_left += node.energy_level
    print(f" Năng lượng còn lại của Node {node.id}: {node.energy_level:.2f}.")

average_energy_left = total_energy_left / number_of_nodes
print(f" Năng lượng trung bình còn lại mỗi node: {average_energy_left:.2f}.")

# Packet Delivery Ratio (PDR): tỉ lệ gửi gói tin thành công
if total_packets_sent > 0:
    pdr = (total_packets_receive / total_packets_sent) * 100
    print(f"Tỉ lệ gửi gói tin thành công (PDR): {pdr:.2f}%")