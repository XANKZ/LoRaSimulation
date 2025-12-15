#include <DHT.h>

// --- CẤU HÌNH ---
// Chân nối Data của DHT22 vào ESP32 (Ví dụ chân D4 - GPIO 4)
// Bạn phải nối dây Data của cảm biến vào chân số 4 trên ESP32
#define DHTPIN 4     

// Chọn loại cảm biến là DHT22
#define DHTTYPE DHT22   

// Khởi tạo cảm biến
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.println("Khoi dong DHT22 tren ESP32...");

  // Bắt đầu đọc cảm biến
  dht.begin();
}

void loop() {
  // Đợi 2 giây giữa các lần đọc (DHT22 đọc khá chậm)
  delay(2000);

  // Đọc độ ẩm
  float h = dht.readHumidity();
  // Đọc nhiệt độ (C)
  float t = dht.readTemperature();

  // Kiểm tra nếu đọc lỗi (kết quả là NaN - Not a Number)
  if (isnan(h) || isnan(t)) {
    Serial.println("Loi: Khong doc duoc du lieu tu cam bien DHT22!");
    Serial.println("Kiem tra lai day tin hieu va nguon (3.3V hoac 5V)");
    return;
  }

  // In kết quả ra màn hình
  Serial.print("Do am: ");
  Serial.print(h);
  Serial.print("%  |  ");
  Serial.print("Nhiet do: ");
  Serial.print(t);
  Serial.println("*C");
}