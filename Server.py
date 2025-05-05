import socket
import psycopg2
from datetime import datetime, timedelta
from dateutil import tz
import pytz

# === Database Config ===
DB_CONFIG = {
    'host': 'ep-frosty-sea-a6uqgpgz-pooler.us-west-2.aws.neon.tech',
    'port': 5432,
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_zbx9eflUnsh5',
    'sslmode': 'require'
}
TABLE = '"data_virtual"'

# === Binary Search Tree for Metadata ===
class TreeNode:
    def __init__(self, key, metadata):
        self.key = key
        self.metadata = metadata
        self.left = None
        self.right = None

def insert(node, key, metadata):
    if node is None:
        return TreeNode(key, metadata)
    if key < node.key:
        node.left = insert(node.left, key, metadata)
    else:
        node.right = insert(node.right, key, metadata)
    return node

def search(node, key):
    if node is None:
        return None
    if key == node.key:
        return node.metadata
    elif key < node.key:
        return search(node.left, key)
    else:
        return search(node.right, key)

# === Build BST ===
def build_metadata_tree():
    metadata_dict = {
        "SmartFridge1": {
            "moisture_sensor": "Moisture Meter - MoistMeter",
            "ammeter": "AmmeterSensor",
            "timezone": "US/Pacific"
        },
        "SmartDishwasher": {
            "water_sensor": "WaterSensor",
            "ammeter": "DishwasherAmmeter",
            "timezone": "US/Pacific"
        },
        "SmartFridge2": {
            "moisture_sensor": "Moisture Meter - MoistMeter",
            "ammeter": "AmmeterSensor",
            "timezone": "US/Pacific"
        }
    }

    root = None
    for device, meta in metadata_dict.items():
        root = insert(root, device, meta)
    return root

# === Helpers ===
def to_pst(epoch):
    dt = datetime.utcfromtimestamp(int(epoch)).replace(tzinfo=pytz.utc)
    pst = dt.astimezone(tz.gettz("US/Pacific"))
    return pst.strftime('%Y-%m-%d %I:%M:%S %p %Z')

def liters_to_gallons(liters):
    return float(liters) * 0.264172

def amps_to_kwh(amps, volts=120, duration_hours=1):
    return float(amps) * volts * duration_hours / 1000

# === Query 1: Avg Moisture (Fridge1, past 3 hrs)
def avg_moisture(cursor, tree):
    device = "SmartFridge1"
    meta = search(tree, device)
    if not meta:
        return "Device metadata not found."

    sensor_key = meta["moisture_sensor"]
    time_cutoff = int((datetime.utcnow() - timedelta(hours=3)).timestamp())

    cursor.execute(f"""
        SELECT AVG(CAST(payload ->> %s AS FLOAT))
        FROM {TABLE}
        WHERE topic = 'Fridge/Board/Sensor'
        AND (payload ->> 'timestamp')::BIGINT > %s
    """, (sensor_key, time_cutoff))

    result = cursor.fetchone()[0]
    return f"Avg {sensor_key} (last 3 hrs): {result:.2f}% RH" if result else "No recent data found."

# === Query 2: Avg Water Use (Dishwasher)
def avg_water(cursor, tree):
    device = "SmartDishwasher"
    meta = search(tree, device)
    if not meta:
        return "Device metadata not found."

    sensor_key = meta["water_sensor"]

    cursor.execute(f"""
        SELECT AVG(CAST(payload ->> %s AS FLOAT))
        FROM {TABLE}
        WHERE topic = 'Fridge/Board/Sensor'
    """, (sensor_key,))
    result = cursor.fetchone()[0]
    return f"Avg water per cycle: {liters_to_gallons(result):.2f} gallons" if result else "No water data available."

# === Query 3: Power Comparison
def compare_power(cursor, tree):
    devices = ["SmartFridge1", "SmartFridge2", "SmartDishwasher"]
    usage = {}

    for device in devices:
        meta = search(tree, device)
        if not meta:
            usage[device] = 0
            continue

        sensor_key = meta["ammeter"]
        cursor.execute(f"""
            SELECT AVG(CAST(payload ->> %s AS FLOAT))
            FROM {TABLE}
            WHERE topic = 'Fridge/Board/Sensor'
        """, (sensor_key,))
        avg_amp = cursor.fetchone()[0]
        usage[device] = amps_to_kwh(avg_amp) if avg_amp else 0

    lines = [f"{dev}: {kwh:.2f} kWh" for dev, kwh in usage.items()]
    most = max(usage.items(), key=lambda x: x[1])[0]
    return "\n".join(lines) + f"\n\nMost electricity used: {most}"

# === Query Routing
QUERY_MAP = {
    "What is the average moisture inside my kitchen fridge in the past three hours?": avg_moisture,
    "What is the average water consumption per cycle in my smart dishwasher?": avg_water,
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?": compare_power
}

# === Main TCP Server
def main():
    server_ip = input("Enter server IP (e.g., 127.0.0.1): ")
    server_port = int(input("Enter port number (e.g., 12345): "))

    metadata_tree = build_metadata_tree()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)
        print(f"Server running on {server_ip}:{server_port}")

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Client connected: {addr}")
            with client_socket:
                while True:
                    query = client_socket.recv(1024).decode()
                    if not query:
                        break

                    print("Query received:", query)
                    if query in QUERY_MAP:
                        result = QUERY_MAP[query](cursor, metadata_tree)
                    else:
                        result = (
                            "Sorry, unsupported query. Try:\n" +
                            "\n".join(f"- {q}" for q in QUERY_MAP)
                        )

                    client_socket.sendall(result.encode())

if __name__ == "__main__":
    main()
