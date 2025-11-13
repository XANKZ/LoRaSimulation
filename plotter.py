# Tệp: plotter.py
import pandas as pd
import matplotlib.pyplot as plt

def plot_pdr_vs_nodes(data):
    """Vẽ biểu đồ PDR theo số lượng Node."""
    plt.figure(figsize=(10, 6)) # Tạo một khung hình vẽ với kích thước 10x6 inches
    plt.plot(data['number_of_nodes'], data['pdr'], marker='o', linestyle='-', color='b')
    
    plt.title('Ảnh hưởng của Số lượng Node đến Tỷ lệ Gửi gói tin Thành công (PDR)')
    plt.xlabel('Số lượng Node trong mạng')
    plt.ylabel('Packet Delivery Ratio (%)')
    plt.grid(True) # Hiển thị lưới
    plt.ylim(0, 105) # Giới hạn trục Y từ 0 đến 105
    plt.xticks(data['number_of_nodes']) # Đảm bảo các điểm trên trục X khớp với dữ liệu
    
    plt.savefig("pdr_vs_nodes.png") # Lưu biểu đồ ra file ảnh
    print("Đã lưu biểu đồ PDR vào file pdr_vs_nodes.png")
    plt.show() # Hiển thị biểu đồ

def plot_packet_breakdown(data):
    """Vẽ biểu đồ cột chồng phân tích các loại gói tin."""
    plt.figure(figsize=(10, 6))
    
    num_nodes = data['number_of_nodes']
    received = data['total_received']
    collisions = data['total_collisions']
    
    # Gói tin bị mất do tín hiệu yếu = Tổng gửi - Nhận thành công - Bị xung đột
    lost_rssi = data['total_sent'] - received - collisions

    # Vẽ các thanh
    plt.bar(num_nodes, received, width=30, label='Thành công')
    plt.bar(num_nodes, collisions, width=30, bottom=received, label='Xung đột')
    plt.bar(num_nodes, lost_rssi, width=30, bottom=received + collisions, label='Mất (Tín hiệu yếu)')

    plt.title('Phân tích Trạng thái Gói tin theo Quy mô Mạng')
    plt.xlabel('Số lượng Node trong mạng')
    plt.ylabel('Số lượng Gói tin')
    plt.legend() # Hiển thị chú thích
    plt.grid(axis='y', linestyle='--')

    plt.savefig("packet_breakdown.png")
    print("Đã lưu biểu đồ phân tích gói tin vào file packet_breakdown.png")
    plt.show()

# --- CHƯƠNG TRÌNH CHÍNH CỦA PLOTTER ---
if __name__ == "__main__":
    input_filename = "result.csv"
    
    try:
        # Đọc dữ liệu từ file CSV bằng pandas
        df_results = pd.read_csv(input_filename)
        print("Đã đọc dữ liệu thành công từ:", input_filename)
        print(df_results) # In bảng dữ liệu ra xem

        # Gọi các hàm để vẽ biểu đồ
        plot_pdr_vs_nodes(df_results)
        plot_packet_breakdown(df_results)

    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy tệp '{input_filename}'.")
        print("Hãy chạy 'python main.py' trước để tạo ra tệp kết quả.")