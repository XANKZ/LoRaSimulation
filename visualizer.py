import pandas as pd
import matplotlib.pyplot as plt
import ast

def parse_position(details_str):
    """
    Hàm phụ trợ để lấy tọa độ (x, y) từ chuỗi details.
    Ví dụ details: "SF = 9, Pos = (831791, 250420)" -> Trả về (831791, 250420)
    """
    try:
        # Tìm phần sau chữ "Pos ="
        pos_part = details_str.split('Pos =')[1].strip()
        # Dùng ast.literal_eval để chuyển chuỗi "(x, y)" thành tuple số học
        return ast.literal_eval(pos_part)
    except (IndexError, ValueError, SyntaxError):
        return None

def visualize_network_map(log_filename, output_image="network_map_final.png"):
    print(f"Đang đọc dữ liệu từ {log_filename}...")
    try:
        # Đọc file CSV
        df = pd.read_csv(log_filename)
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file '{log_filename}'. Hãy chạy main.py trước.")
        return

    # 1. Lấy danh sách Node và vị trí của chúng (từ sự kiện INIT)
    print("Đang xử lý vị trí các Node...")
    node_positions = {}
    
    # Lọc các dòng có event_type là 'INIT'
    init_events = df[df['event_type'] == 'INIT']
    
    if init_events.empty:
        print("LỖI: Không tìm thấy sự kiện INIT trong file log. File log có thể bị lỗi.")
        return

    for _, row in init_events.iterrows():
        pos = parse_position(row['details'])
        if pos:
            node_positions[row['node_id']] = pos

    if not node_positions:
        print("LỖI: Không phân tích được vị trí node nào cả.")
        return

    # 2. Xác định trạng thái cuối cùng của từng Node (để tô màu)
    # Lấy dòng log cuối cùng của mỗi node_id
    last_status = df.drop_duplicates(subset=['node_id'], keep='last').set_index('node_id')

    # 3. Lấy vị trí Gateway (Cần khớp với main.py, hoặc lấy từ log nếu có log gateway init)
    # Ở đây ta hard-code tạm thời theo tỷ lệ 100 hecta (1000x1000m) 
    # Nếu main.py bạn sửa thành 1000 thì ở đây phải là 250 và 750
    # ĐỂ AN TOÀN: Ta sẽ tự động tính dựa trên Max tọa độ của Node
    all_x = [p[0] for p in node_positions.values()]
    all_y = [p[1] for p in node_positions.values()]
    max_w = max(all_x) if all_x else 1000
    max_h = max(all_y) if all_y else 1000
    
    gateway_positions = {
        0: (max_w * 0.25, max_h * 0.25),
        1: (max_w * 0.25, max_h * 0.75),
        2: (max_w * 0.75, max_h * 0.25),
        3: (max_w * 0.75, max_h * 0.75)
    }

    # --- BẮT ĐẦU VẼ ---
    plt.figure(figsize=(12, 12)) # Kích thước ảnh
    ax = plt.gca()

    # A. Vẽ các đường kết nối (Chỉ vẽ những kết nối thành công cuối cùng để đỡ rối)
    print("Đang vẽ các kết nối...")
    success_events = df[df['event_type'] == 'TRANSMIT_SUCCESS']
    # Lấy kết nối thành công gần nhất của mỗi node
    last_connections = success_events.drop_duplicates(subset=['node_id'], keep='last')

    for _, row in last_connections.iterrows():
        node_id = row['node_id']
        gw_id_raw = row['gateway_id'] # Có thể là float hoặc string "0.0"
        
        try:
            gw_id = int(float(gw_id_raw)) # Chuyển về int an toàn
            
            if node_id in node_positions and gw_id in gateway_positions:
                n_pos = node_positions[node_id]
                g_pos = gateway_positions[gw_id]
                
                # Vẽ đường nét đứt màu xám nhạt
                plt.plot([n_pos[0], g_pos[0]], [n_pos[1], g_pos[1]], 
                         color='gray', linestyle=':', linewidth=0.5, alpha=0.6, zorder=1)
        except:
            continue

    # B. Vẽ Gateways
    print("Đang vẽ Gateway...")
    for gid, pos in gateway_positions.items():
        plt.scatter(pos[0], pos[1], s=300, c='red', marker='^', edgecolors='black', zorder=10, label='Gateway' if gid==0 else "")
        plt.text(pos[0], pos[1]+(max_h*0.02), f"GW{gid}", ha='center', fontsize=10, fontweight='bold', color='darkred')

    # C. Vẽ Nodes
    print("Đang vẽ Nodes...")
    count_dead = 0
    count_alive = 0
    
    for nid, pos in node_positions.items():
        # Kiểm tra trạng thái cuối
        status_row = last_status.loc[nid] if nid in last_status.index else None
        
        color = 'green' # Mặc định sống
        label = 'Node'
        
        if status_row is not None:
            event = status_row['event_type']
            energy = float(status_row['energy_level']) if status_row['energy_level'] != '' else 0
            
            if event == 'DEAD' or energy <= 0:
                color = 'black' # Chết
                count_dead += 1
            elif energy < 20000: # Ví dụ pin yếu (dưới 20%)
                color = 'orange'
                count_alive += 1
            else:
                color = 'blue'
                count_alive += 1
        
        # Vẽ điểm
        plt.scatter(pos[0], pos[1], s=60, c=color, edgecolors='white', zorder=5)
        # Có thể hiện ID nếu muốn (sẽ hơi rối nếu 100 node)
        # plt.text(pos[0], pos[1], str(nid), fontsize=8)

    # D. Hoàn thiện biểu đồ
    plt.title(f"Bản đồ Mạng LoRaWAN (100 Hecta)\nNode Sống: {count_alive} | Node Chết: {count_dead}", fontsize=14)
    plt.xlabel("Khoảng cách (mét)")
    plt.ylabel("Khoảng cách (mét)")
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Tạo chú thích giả (Legend)
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='^', color='w', label='Gateway', markerfacecolor='red', markersize=15),
        Line2D([0], [0], marker='o', color='w', label='Node (Pin Tốt)', markerfacecolor='blue', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Node (Pin Yếu)', markerfacecolor='orange', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Node (Chết)', markerfacecolor='black', markersize=10),
        Line2D([0], [0], color='gray', linestyle=':', label='Kết nối thành công')
    ]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.axis('equal') # Quan trọng: Giữ tỷ lệ 1:1 cho bản đồ không bị méo
    plt.tight_layout()
    
    plt.savefig(output_image, dpi=300) # Lưu ảnh chất lượng cao
    print(f"XONG! Đã lưu bản đồ vào file: {output_image}")
    plt.show()

if __name__ == "__main__":
    # Thay tên file log của bạn vào đây
    LOG_FILE = "log_100_nodes.csv" 
    visualize_network_map(LOG_FILE)