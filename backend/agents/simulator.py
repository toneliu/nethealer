import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class MockSyslogEntry:
    timestamp: str
    source: str
    severity: str
    message: str
    interface: str = None


class SyslogSimulator:
    def __init__(self):
        self.devices = ["acc-02", "acc-01", "dist-01", "dist-02", "core-01"]
        self.severities = ["info", "warning", "error", "critical"]

        self.templates = [
            ("info", "%LINEPROTO-5-UPDOWN: Interface {iface}, changed state to up"),
            ("info", "%LINEPROTO-5-UPDOWN: Interface {iface}, changed state to down"),
            ("warning", "%SYS-5-CONFIG_I: Configured from console"),
            ("error", "%INTERFACE-3-ERROR: {iface} CRC errors increased from 0.01% to 2.3%"),
            ("error", "%INTERFACE-3-ERROR: {iface} input queue full"),
            ("warning", "%PORT_SECURITY-2-PSECURE_VIOLATION: Security violation occurred"),
            ("info", "%SPANTREE-5-TOPOTYPE: Topology change detected on {iface}"),
            ("warning", "%LINK-3-UPDOWN: Interface {iface}, port error disabled"),
            ("error", "%ILPOWER-3-PRES_DETECT: Interface {iface}: Power Device Detect failure"),
            ("info", "%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch detected on {iface}"),
        ]

        self.interfaces = [
            "GigabitEthernet0/1",
            "GigabitEthernet0/2",
            "GigabitEthernet0/3",
            "GigabitEthernet0/4",
            "FastEthernet0/1"
        ]

        self.critical_templates = [
            ("error", "%INTERFACE-3-ERROR: Interface GigabitEthernet0/1: CRC errors increased from 0.01% to 2.3%"),
            ("error", "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, port error disabled"),
        ]

    def generate_logs(self, count: int = 10) -> List[MockSyslogEntry]:
        logs = []
        base_time = datetime.now()

        critical_log = MockSyslogEntry(
            timestamp=base_time.isoformat(),
            source="acc-02",
            severity="error",
            message="%INTERFACE-3-ERROR: Interface GigabitEthernet0/1: CRC errors increased from 0.01% to 2.3%",
            interface="GigabitEthernet0/1"
        )
        logs.append(critical_log)

        for i in range(count - 1):
            time_offset = timedelta(seconds=i * 3)
            timestamp = (base_time - time_offset).isoformat()

            template = random.choice(self.templates)
            severity, message_template = template

            interface = random.choice(self.interfaces)
            message = message_template.format(iface=interface)

            device = random.choice(self.devices)

            if i < 3:
                device = "acc-02"
                severity = "error" if i == 0 else "warning"

            logs.append(MockSyslogEntry(
                timestamp=timestamp,
                source=device,
                severity=severity,
                message=message,
                interface=interface
            ))

        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs


class SNMPSimulator:
    def __init__(self):
        self.devices = ["acc-02", "acc-01", "dist-01", "dist-02", "core-01", "fw-01", "router-01"]

        self.metrics = {
            "ifInErrors": {"normal": (10, 100), "anomaly": (5000, 25000)},
            "ifOutErrors": {"normal": (5, 50), "anomaly": (1000, 5000)},
            "ifInUcastPkts": {"normal": (10000, 50000), "anomaly": (5000, 15000)},
            "ifOutUcastPkts": {"normal": (10000, 50000), "anomaly": (5000, 15000)},
            "ifSpeed": {"normal": (1000000000,), "anomaly": (1000000000,)},
            "ifOperStatus": {"normal": (1,), "anomaly": (2,)},
            "cpuUtilization": {"normal": (20, 60), "anomaly": (80, 95)},
            "memUtilization": {"normal": (40, 70), "anomaly": (80, 95)},
            "temperature": {"normal": (35, 55), "anomaly": (65, 85)}
        }

    def generate_metrics(self, devices: List[str] = None) -> List[Dict]:
        if devices is None:
            devices = self.devices

        metrics = []
        base_time = datetime.now()

        acc02_anomaly_metrics = [
            {
                "timestamp": base_time.isoformat(),
                "device": "acc-02",
                "metric_name": "ifInErrors",
                "value": random.randint(20000, 25000),
                "threshold": 100
            },
            {
                "timestamp": base_time.isoformat(),
                "device": "acc-02",
                "metric_name": "ifOutErrors",
                "value": random.randint(5000, 8000),
                "threshold": 50
            },
            {
                "timestamp": base_time.isoformat(),
                "device": "acc-02",
                "metric_name": "packetLoss",
                "value": random.uniform(4.5, 6.0),
                "threshold": 1.0
            }
        ]
        metrics.extend(acc02_anomaly_metrics)

        for device in devices:
            if device == "acc-02":
                continue

            for metric_name, ranges in self.metrics.items():
                is_anomaly = random.random() < 0.1

                if is_anomaly:
                    value_range = ranges["anomaly"]
                    threshold = ranges["normal"][0] * 0.5 if len(ranges["normal"]) > 0 else 0
                else:
                    value_range = ranges["normal"]
                    threshold = value_range[0] * 2 if len(value_range) > 0 else 0

                if len(value_range) == 1:
                    value = value_range[0]
                else:
                    value = random.uniform(value_range[0], value_range[1])
                if metric_name in ["ifOperStatus"]:
                    value = 1 if not is_anomaly else 2

                metrics.append({
                    "timestamp": (base_time - timedelta(minutes=random.randint(1, 30))).isoformat(),
                    "device": device,
                    "metric_name": metric_name,
                    "value": round(value, 2),
                    "threshold": round(threshold, 2)
                })

        return metrics


class TopologySimulator:
    def __init__(self):
        self.topology = {
            "nodes": [
                {"id": "router-01", "name": "边界路由器", "type": "router", "neighbors": ["fw-01"]},
                {"id": "fw-01", "name": "防火墙", "type": "firewall", "neighbors": ["core-01"]},
                {"id": "core-01", "name": "核心交换机", "type": "core", "neighbors": ["fw-01", "dist-01", "dist-02"]},
                {"id": "dist-01", "name": "汇聚交换机-A", "type": "distribution", "neighbors": ["core-01", "acc-01", "acc-02", "acc-03"]},
                {"id": "dist-02", "name": "汇聚交换机-B", "type": "distribution", "neighbors": ["core-01", "acc-03", "acc-04", "acc-05"]},
                {"id": "acc-01", "name": "接入交换机-1", "type": "access", "neighbors": ["dist-01"]},
                {"id": "acc-02", "name": "接入交换机-2", "type": "access", "neighbors": ["dist-01"], "status": "error"},
                {"id": "acc-03", "name": "接入交换机-3", "type": "access", "neighbors": ["dist-01", "dist-02"]},
                {"id": "acc-04", "name": "接入交换机-4", "type": "access", "neighbors": ["dist-02"]},
                {"id": "acc-05", "name": "接入交换机-5", "type": "access", "neighbors": ["dist-02"]},
            ],
            "links": [
                {"source": "router-01", "target": "fw-01", "bandwidth": "10G", "status": "active"},
                {"source": "fw-01", "target": "core-01", "bandwidth": "10G", "status": "active"},
                {"source": "core-01", "target": "dist-01", "bandwidth": "10G", "status": "active"},
                {"source": "core-01", "target": "dist-02", "bandwidth": "10G", "status": "active"},
                {"source": "dist-01", "target": "acc-01", "bandwidth": "1G", "status": "active"},
                {"source": "dist-01", "target": "acc-02", "bandwidth": "1G", "status": "degraded"},
                {"source": "dist-01", "target": "acc-03", "bandwidth": "1G", "status": "active"},
                {"source": "dist-02", "target": "acc-03", "bandwidth": "1G", "status": "active"},
                {"source": "dist-02", "target": "acc-04", "bandwidth": "1G", "status": "active"},
                {"source": "dist-02", "target": "acc-05", "bandwidth": "1G", "status": "active"},
            ],
            "alerts": [
                {"nodeId": "acc-02", "type": "error", "message": "端口CRC错误"}
            ]
        }

    def get_topology(self) -> Dict:
        return self.topology

    def get_node_status(self, node_id: str) -> Dict:
        for node in self.topology["nodes"]:
            if node["id"] == node_id:
                return node
        return None

    def get_link_status(self, source: str, target: str) -> Dict:
        for link in self.topology["links"]:
            if (link["source"] == source and link["target"] == target) or \
               (link["source"] == target and link["target"] == source):
                return link
        return None
