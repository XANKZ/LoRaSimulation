import csv
import os

class Logger:
    def __init__(self, filename = "node_activity_log.csv"):
        self.filename = filename
        self.fieldnames = [
            'timestamp',
            'node_id',
            'event_type',
            'details',
            'energy_level',
            'rssi',
            'gateway_id'
        ]

        if os.path.exists(self.filename):
            os.remove(self.filename)

        self.file = open(self.filename, 'w', newline = '', encoding = 'utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames = self.fieldnames)
        self.writer.writeheader()

        self.file.flush()
        
        # with open(self.filename, 'w', newline = '', encoding = 'utf-8') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
        #     writer.writeheader()

    def log(self, timestamp, node_id, event_type, details = "", energy_level = None, rssi = None, gateway_id = None):
        self.writer.writerow(
            {   'timestamp':timestamp,
                'node_id': node_id,
                'event_type': event_type,
                'details': details,
                'energy_level': f"{energy_level:.2f}" if energy_level is not None else "",
                'rssi': f"{rssi:.2f}" if rssi is not None else "",
                'gateway_id': gateway_id if gateway_id is not None else ""
            }
        )

    def close(self):
        if self.file:
            self.file.close()