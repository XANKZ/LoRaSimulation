from Node import Node
from Gateway import Gateway
from Channel import calculate_rssi
from ChannelManager import ChannelManager
import random
import csv

print("Bắt đầu chương trình mô phỏng.")


def run_simulation(number_of_nodes, duration_seconds):
    print(f"\nBắt đầu kịch vạn với {number_of_nodes} Node.")

    FARM_WIDTH = 1000000
    FARM_HEIGHT = 1000000

    nodes = []

    for i in range(number_of_nodes):
        random_x = random.randint(0,FARM_WIDTH)
        random_y = random.randint(0,FARM_HEIGHT)

        assigned_sf = random.choice([7, 8, 9, 10, 11, 12])
        # Cái này thực tế được điều khiển bới ADR nhưng nếu có thuật toán thì cần sửa đổi

        new_node = Node(node_id = i, x = random_x, y = random_y, sf = assigned_sf)
        nodes.append(new_node)

    gateways = [
        Gateway(gateway_id = 0, x = FARM_WIDTH * 0.25 , y = FARM_HEIGHT * 0.25),
        Gateway(gateway_id = 1, x = FARM_WIDTH * 0.25 , y = FARM_HEIGHT * 0.75),
        Gateway(gateway_id = 2, x = FARM_WIDTH * 0.75 , y = FARM_HEIGHT * 0.25),
        Gateway(gateway_id = 3, x = FARM_WIDTH * 0.75 , y = FARM_HEIGHT * 0.75)
    ]

    channel_manager = ChannelManager(num_channels = 1)
    # Cần nghiên cứu lại chỗ này, không biết chắc là LoRa có hoạt động như vậy không

    print("\nĐã khởi tạo xong Node và Gateway. Bắt đầu vòng lặp thời gian...")

    total_packets_sent = 0
    total_packets_received = 0
    total_collisions = 0

    for time_step in range(duration_seconds):
        # if time_step %3600 == 0:
        #     print(f" Giờ thứ {time_step // 3600}.")
        for node in nodes:
            packet = node.update(time_step)

            if packet:
                total_packets_sent += 1

                is_collided = channel_manager.check_collision(packet, time_step)
                if is_collided:
                    total_collisions += 1
                    continue
                #print(f"!!! Thời gian {time_step}s: Node {node.id} đang phát gói tin.")

                is_receive_by_any_gw = False
                
                for gw in gateways:
                    rssi = calculate_rssi(node, gw)
                    if gw.receive_packet(packet, rssi):
                        is_receive_by_any_gw = True
                        break
                
                if is_receive_by_any_gw:
                    total_packets_received += 1

    total_energy_left = sum(node.energy_level for node in nodes)

    average_energy_left = total_energy_left / number_of_nodes

    # Packet Delivery Ratio (PDR): tỉ lệ gửi gói tin thành công
    if total_packets_sent > 0:
        pdr = (total_packets_received / total_packets_sent) * 100
        print(f"Tỉ lệ gửi gói tin thành công (PDR): {pdr:.2f}%")
    else:
        pdr = 0

    result = {
            "number_of_nodes": number_of_nodes,
            "total_sent": total_packets_sent,
            "total_received": total_packets_received,
            "total_collisions": total_collisions,
            "pdr": pdr,
            "avg_energy_left": average_energy_left
        }
    return result

if __name__ == "__main__":
    node_scenarios = [100]
    duration_seconds = 86400

    all_result = []

    for n_nodes in node_scenarios:
        scenario_result = run_simulation(n_nodes, duration_seconds)
        all_result.append(scenario_result)
        print(f"Kết quả: PDR = {scenario_result['pdr']:.2f}%, Xung đột = {scenario_result['total_collisions']}.")

        output_filename = "result.csv"
        headers = all_result[0].keys()

        with open(output_filename, 'w', newline='',encoding = 'utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = headers)
            writer.writeheader()
            writer.writerows(all_result)
        print(f"Đã lưu tất cả kết quả vào tệp: {output_filename}.")

print("\nKết thúc mô phỏng.")
print(f" Tổng thời gian mô phỏng: {duration_seconds / 3600:.1f} giờ.")
print(f" Tổng các gói tin đẫ nhận được bởi các node: {all_result[-1]['total_sent']}.")
print(f" Tổng các gói tin đã nhận bởi gateway: {all_result[-1]['total_received']}.")
