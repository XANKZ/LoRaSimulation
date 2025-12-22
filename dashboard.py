import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ast
import time
import numpy as np

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="LoRaWAN Sim Dashboard", layout="wide")
st.title("📊 Dashboard Mô phỏng Mạng LoRaWAN")

# --- 1. HÀM PHỤ TRỢ & LOAD DỮ LIỆU ---
def parse_position(details_str):
    """Trích xuất tọa độ (x, y) từ chuỗi details."""
    try:
        if isinstance(details_str, str) and 'Pos =' in details_str:
            pos_part = details_str.split('Pos =')[1].strip()
            return ast.literal_eval(pos_part)
    except:
        pass
    return None

@st.cache_data
def load_data(csv_file):
    """
    Đọc file CSV và xử lý sơ bộ:
    1. Sắp xếp theo thời gian (Quan trọng để chạy mượt).
    2. Xử lý các cột số (Energy, Gateway ID) để tránh lỗi NaN.
    """
    try:
        df = pd.read_csv(csv_file)
        
        # Tối ưu 1: Sắp xếp ngay từ đầu
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
            
        # Tối ưu 2: Ép kiểu số cho cột năng lượng, điền 0 nếu lỗi/trống
        if 'energy_level' in df.columns:
            df['energy_level'] = pd.to_numeric(df['energy_level'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error(f"Không thể đọc file: {e}")
        return None

# --- 2. SIDEBAR & INPUT ---
st.sidebar.header("📁 Cấu hình Dữ liệu")
default_file = "log_100_nodes.csv"
log_file = st.sidebar.text_input("Đường dẫn file log:", default_file)

# Nút reload để xóa cache nếu file thay đổi
if st.sidebar.button("🔄 Tải lại dữ liệu"):
    st.cache_data.clear()
    st.rerun()

df = load_data(log_file)

if df is not None:
    # --- 3. KHỞI TẠO VỊ TRÍ (NODE & GATEWAY) ---
    # Chỉ chạy 1 lần dựa trên dữ liệu đã cache
    init_events = df[df['event_type'] == 'INIT']
    node_positions = {}
    for _, row in init_events.iterrows():
        pos = parse_position(row['details'])
        if pos:
            node_positions[row['node_id']] = pos
            
    # Xác định kích thước bản đồ
    if node_positions:
        all_x = [p[0] for p in node_positions.values()]
        all_y = [p[1] for p in node_positions.values()]
        max_w = max(all_x) * 1.1 # Thêm 10% lề
        max_h = max(all_y) * 1.1
    else:
        max_w, max_h = 1000, 1000

    # Cấu hình vị trí Gateway (Giả lập cố định 4 góc)
    gateway_positions = {
        0: (max_w * 0.25, max_h * 0.25),
        1: (max_w * 0.25, max_h * 0.75),
        2: (max_w * 0.75, max_h * 0.25),
        3: (max_w * 0.75, max_h * 0.75)
    }

    # --- 4. ĐIỀU KHIỂN PLAYBACK ---
    max_time = int(df['timestamp'].max())
    
    # Khởi tạo Session State
    if 'slider_time' not in st.session_state:
        st.session_state.slider_time = 0
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False

    st.sidebar.markdown("---")
    st.sidebar.header("⏯️ Điều khiển Mô phỏng")
    
    col_btn1, col_btn2 = st.sidebar.columns(2)
    if col_btn1.button("▶️ Chạy", use_container_width=True):
        st.session_state.is_playing = True
    if col_btn2.button("⏸️ Dừng", use_container_width=True):
        st.session_state.is_playing = False

    # Chọn bước nhảy thời gian
    speed = st.sidebar.select_slider(
        "Tốc độ (Giây mô phỏng / Khung hình):", 
        options=[60, 300, 600, 1800, 3600], 
        value=300
    )

    # Logic tự động tăng thời gian
    if st.session_state.is_playing:
        if st.session_state.slider_time < max_time:
            st.session_state.slider_time += speed
            # Kiểm tra biên
            if st.session_state.slider_time > max_time:
                st.session_state.slider_time = max_time
                st.session_state.is_playing = False
        else:
            st.session_state.is_playing = False # Dừng khi hết giờ

    # Slider hiển thị thời gian (Kết nối 2 chiều với session_state)
    current_t = st.sidebar.slider(
        "Thanh thời gian:", 
        min_value=0, max_value=max_time, step=60,
        key="slider_time" # Key này cực quan trọng để đồng bộ
    )

    # --- 5. XỬ LÝ DỮ LIỆU TẠI THỜI ĐIỂM T ---
    # Lọc dữ liệu tính đến thời điểm hiện tại
    df_current = df[df['timestamp'] <= current_t]
    
    # Tính toán trạng thái
    if not df_current.empty:
        # Groupby lấy dòng cuối cùng của mỗi node
        latest_status = df_current.groupby('node_id').last()
        active_count = len(latest_status[latest_status['event_type'] != 'DEAD'])
        dead_count = len(latest_status[latest_status['event_type'] == 'DEAD'])
    else:
        latest_status = pd.DataFrame()
        active_count, dead_count = 0, 0
        
    pdr_count = len(df_current[df_current['event_type'] == 'TRANSMIT_SUCCESS'])
    collision_count = len(df_current[df_current['event_type'] == 'COLLISION'])

    # --- 6. HIỂN THỊ GIAO DIỆN ---
    
    # 6.1 Hiển thị Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Node Hoạt động", active_count)
    m2.metric("Node Đã chết", dead_count, delta_color="inverse")
    m3.metric("Gói tin Thành công", pdr_count)
    m4.metric("Xung đột", collision_count, delta_color="inverse")

    st.markdown(f"### 🕒 Thời gian: **{current_t // 3600}h {(current_t % 3600) // 60}m**")

    # 6.2 Vẽ Biểu đồ (Plotly)
    fig = go.Figure()

    # LAYER 1: Kết nối (Chỉ hiện kết nối MỚI trong 1h gần nhất để đỡ rối)
    recent_success = df_current[
        (df_current['event_type'] == 'TRANSMIT_SUCCESS') & 
        (df_current['timestamp'] > current_t - 3600)
    ]
    
    if not recent_success.empty:
        last_connections = recent_success.groupby('node_id').last()
        edge_x, edge_y = [], []
        
        for node_id, row in last_connections.iterrows():
            if node_id in node_positions:
                try:
                    # Kiểm tra an toàn Gateway ID
                    if pd.notna(row['gateway_id']):
                        gw_id = int(float(row['gateway_id']))
                        if gw_id in gateway_positions:
                            n_pos = node_positions[node_id]
                            g_pos = gateway_positions[gw_id]
                            edge_x.extend([n_pos[0], g_pos[0], None])
                            edge_y.extend([n_pos[1], g_pos[1], None])
                except: continue

        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='rgba(150, 150, 150, 0.5)'), # Màu xám mờ
            hoverinfo='none', mode='lines', name='Kết nối (1h qua)'
        ))

    # LAYER 2: Gateways
    gw_x = [pos[0] for pos in gateway_positions.values()]
    gw_y = [pos[1] for pos in gateway_positions.values()]
    fig.add_trace(go.Scatter(
        x=gw_x, y=gw_y,
        mode='markers+text',
        marker=dict(symbol='triangle-up', size=18, color='red', line=dict(width=1, color='black')),
        text=[f"GW {k}" for k in gateway_positions.keys()],
        textposition="top center", name='Gateway'
    ))

    # LAYER 3: Nodes
    if node_positions:
        node_x, node_y, node_colors, node_texts = [], [], [], []
        
        for node_id, pos in node_positions.items():
            node_x.append(pos[0])
            node_y.append(pos[1])
            
            # Mặc định
            color = 'gray'
            status = "INIT"
            energy_val = 100000

            # Cập nhật trạng thái nếu có dữ liệu
            if not latest_status.empty and node_id in latest_status.index:
                row = latest_status.loc[node_id]
                state = row['event_type']
                energy_val = row['energy_level'] # Đã xử lý fillna(0) ở load_data
                
                if state == 'DEAD' or energy_val <= 0:
                    color = 'black'
                    status = "DEAD"
                elif energy_val < 20000:
                    color = 'orange'
                    status = "LOW BATTERY"
                else:
                    color = '#00CC96' # Xanh lá đẹp hơn
                    status = "ACTIVE"
            
            node_colors.append(color)
            node_texts.append(f"<b>Node {node_id}</b><br>Status: {status}<br>Pin: {energy_val:.0f}")

        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(size=8, color=node_colors, line=dict(width=1, color='white')),
            text=node_texts, hoverinfo='text', name='Node'
        ))

    fig.update_layout(
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=True, title='Mét (X)'),
        yaxis=dict(showgrid=True, title='Mét (Y)', scaleanchor="x", scaleratio=1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 7. VÒNG LẶP RERUN (ĐẶT Ở CUỐI CÙNG) ---
    if st.session_state.is_playing:
        # Quan trọng: Ngủ đủ lâu để trình duyệt render xong hình ảnh (0.2s - 0.5s)
        time.sleep(0.2) 
        st.rerun()

else:
    st.info("👈 Hãy nhập tên file log chính xác ở thanh bên trái.")