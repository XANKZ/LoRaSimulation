# Long distance Path Loss model
import math

P_TX = 14.0     # Công suất của Node 14dBm
PL_D0 = 40.0    # Suy hao tín hiệu tại tham chiếu d0 ( ví dụ 40 dBm tại 1m)
D0 = 1.0        # Khoảng cách tham chiếu 1m
GAMMA = 2.5     # Hằng số suy hao đường truyền (path loss exponent)

def calculate_distance(node, gateway):
    # Distance = \sqrt{(x_N - x_G)^2 + (y_N - y_G)^2}
    dist = math.sqrt( (node.pos[0] - gateway.pos[0])**2 + (node.pos[1] - gateway.pos[1])**2 )
    return dist

def calculate_rssi(node, gateway):
    distance = calculate_distance(node,gateway)

    if distance < D0:
        return P_TX - PL_D0
    # \text{PL}(d) \quad [\text{dB}] = \text{PL}_{\text{D0}} + 10 \cdot \gamma \cdot \log_{10} \left( \frac{d}{d_0} \right)
    path_loss = PL_D0 + 10 * GAMMA * math.log10(distance/D0)
    # \text{RSSI} \quad [\text{dBm}] = \text{P}_{\text{TX}} \quad [\text{dBm}] - \text{PL}(d) \quad [\text{dB}]
    rssi = P_TX - path_loss
    return rssi 