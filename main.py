from Node import Node
from Gateway import Gateway
from Channel import calculate_rssi
from ChannelManager import ChannelManager
import random
import csv
from Logger import Logger
from tqdm import tqdm

print("Bắt đầu chương trình mô phỏng.")


def run_simulation(number_of_nodes, duration_seconds):
    print(f"\nBắt đầu kịch vạn với {number_of_nodes} Node.")

    FARM_WIDTH = 1000
    FARM_HEIGHT = 1000

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

    logger = Logger(filename = f"log_{number_of_nodes}_nodes.csv")

    node_positions = {}

    for node in nodes:
        node_positions[node.id] = node.pos
        logger.log(
            timestamp = 0,
            node_id = node.id,
            event_type = "INIT",
            details = f"SF = {node.sf}, Pos = {node.pos}",
            energy_level = node.energy_level
        )

    for time_step in tqdm(range(duration_seconds), mininterval = 1.0, desc = "Simulating"):
        active_nodes = [n for n in nodes if n.state != "SLEEP" or time_step >= n.next_wake_up_time]
        
        if not active_nodes:
            continue

        for node in nodes:
            # gọi method trên instance
            node_result = node.update_and_get_log(time_step)

            for log_entry in node_result.get('logs', []):
                logger.log(timestamp = time_step,
                        node_id = node.id,
                        event_type = log_entry.get('event'),
                        details = log_entry.get('details', ''),
                        energy_level = node.energy_level)
            packet = node_result.get('packet')

            if packet:
                total_packets_sent += 1

                is_collided = channel_manager.check_collision(packet, time_step)
                if is_collided:
                    total_collisions += 1
                    logger.log(timestamp = time_step,
                            node_id = node.id,
                            event_type = "COLLISION",
                            details = f"Xung đột trên kênh {packet['channel']}/SF{packet['sf']}",
                            energy_level = node.energy_level)
                    continue
                #print(f"!!! Thời gian {time_step}s: Node {node.id} đang phát gói tin.")

                best_gateway_id = None
                best_rssi = -999

                #is_receive_by_any_gw = False
                
                for gw in gateways:
                    rssi = calculate_rssi(node, gw)
                    if gw.receive_packet(packet, rssi):
                        if rssi > best_rssi:
                            best_rssi = rssi
                            best_gateway_id = gw.id
                            #is_receive_by_any_gw = True
                
                #if is_receive_by_any_gw:
                if best_gateway_id is not None:
                    total_packets_received += 1
                    logger.log(timestamp = time_step,
                            node_id = node.id,
                                event_type = "TRANSMIT_SUCCESS",
                                details = f"Dữ liệu; {packet['data']}",
                            energy_level = node.energy_level,
                                rssi = best_rssi,
                                gateway_id = best_gateway_id)
                else:
                    logger.log(timestamp = time_step,
                            node_id = node.id,
                            event_type = "TRANSMIT_FAIL_RSSI",
                            details = "Không có gateway nào trong tầm phủ sóng.",
                            energy_level = node.energy_level)
    logger.close()                        

    # Packet Delivery Ratio (PDR): tỉ lệ gửi gói tin thành công

    result = {
            "number_of_nodes": number_of_nodes,
            "total_sent": total_packets_sent,
            "total_received": total_packets_received,
            "total_collisions": total_collisions,
            "pdr": (total_packets_received / total_packets_sent) * 100 if total_packets_sent > 0 else 0,
            "avg_energy_left": (sum(node.energy_level for node in nodes) / number_of_nodes) if number_of_nodes > 0 else 0,
            "node_positions": node_positions,
            "gateway_positions": {gw.id: gw.pos for gw in gateways}
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
