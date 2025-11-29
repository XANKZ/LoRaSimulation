# Tệp: visualizer.py
import pandas as pd
import matplotlib.pyplot as plt
import ast # Thư viện để chuyển chuỗi thành dictionary/tuple

def visualize_network_map(log_filename, node_positions, gateway_positions):
    try:
        df = pd.read_csv(log_filename)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file log '{log_filename}'. Hãy chạy main.py trước.")
        return

    plt.figure(figsize=(12, 12))
    
    # 1. Vẽ vị trí các Gateway
    gw_x = [pos[0] for pos in gateway_positions.values()]
    gw_y = [pos[1] for pos in gateway_positions.values()]
    plt.scatter(gw_x, gw_y, s=200, c='red', marker='^', label='Gateway', zorder=5)
    for gw_id, pos in gateway_positions.items():
        plt.text(pos[0], pos[1] + 20, f'GW {gw_id}', ha='center', color='red')

    # 2. Vẽ vị trí các Node
    node_x = [pos[0] for pos in node_positions.values()]
    node_y = [pos[1] for pos in node_positions.values()]
    plt.scatter(node_x, node_y, s=50, c='blue', marker='o', label='Node')

    # 3. Vẽ các đường kết nối
    # Lọc ra các sự kiện gửi tin thành công
    successful_transmissions = df[df['event_type'] == 'TRANSMIT_SUCCESS'].copy()
    
    # Chỉ lấy kết nối cuối cùng của mỗi node để biểu đồ không bị rối
    last_connections = successful_transmissions.drop_duplicates(subset='node_id', keep='last')

    for index, row in last_connections.iterrows():
        node_id = row['node_id']
        gw_id = int(row['connected_gateway_id'])
        
        node_pos = node_positions[node_id]
        gw_pos = gateway_positions[gw_id]
        
        # Vẽ đường nối
        plt.plot([node_pos[0], gw_pos[0]], [node_pos[1], gw_pos[1]], 
                 linestyle='--', color='gray', linewidth=0.8)

    plt.title('Bản đồ Mạng và Kết nối Gần nhất')
    plt.xlabel('Tọa độ X (mét)')
    plt.ylabel('Tọa độ Y (mét)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal') # Đảm bảo tỉ lệ x và y bằng nhau
    plt.savefig("network_map.png")
    print("Đã lưu bản đồ mạng vào file network_map.png")
    plt.show()

if __name__ == "__main__":
    
    NUM_NODES_TO_VISUALIZE = 100 # Sửa số này khớp với kịch bản bạn đã chạy
    LOG_FILE = f"log_{NUM_NODES_TO_VISUALIZE}_nodes.csv"
    
    # Đọc lại vị trí từ file log để không cần hard-code
    try:
        df_init = pd.read_csv(LOG_FILE)
        node_positions = {}
        # Lấy dòng init của mỗi node
        init_events = df_init[df_init['event_type'] == 'INIT']
        for index, row in init_events.iterrows():
            # ast.literal_eval dùng để chuyển chuỗi '(x, y)' thành tuple (x, y)
            node_positions[row['node_id']] = ast.literal_eval(row['details'].split('Pos=')[1])
        
        # Giả định vị trí gateway (có thể lưu vào file nếu muốn)
        gateway_positions = {
            0: (250, 250),
            1: (250, 750),
            2: (750, 250),
            3: (750, 750)
        }
        
        visualize_network_map(LOG_FILE, node_positions, gateway_positions)

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{LOG_FILE}'.")
        print("Vui lòng chạy 'python main.py' với số node tương ứng trước.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")