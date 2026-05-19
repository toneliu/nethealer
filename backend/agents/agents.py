from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class SyslogEntry:
    timestamp: str
    source: str
    severity: str
    message: str
    interface: Optional[str] = None


@dataclass
class SNMPMetric:
    timestamp: str
    device: str
    metric_name: str
    value: float
    threshold: Optional[float] = None


@dataclass
class NetworkNode:
    id: str
    name: str
    type: str
    neighbors: List[str]
    status: str = "healthy"


@dataclass
class NetworkLink:
    source: str
    target: str
    bandwidth: str
    status: str = "active"


@dataclass
class FaultEvidence:
    type: str
    content: str
    timestamp: str
    device: Optional[str] = None
    confidence: float = 1.0


@dataclass
class RootCause:
    device: str
    device_name: str
    port: Optional[str]
    issue: str
    confidence: float
    evidence_chain: List[FaultEvidence]


@dataclass
class RepairAction:
    id: int
    action: str
    command: str
    description: str
    auto_execute: bool
    status: str = "pending"


class AgentState(TypedDict):
    step: int
    data_collection_complete: bool
    logs: List[Dict]
    metrics: List[Dict]
    topology: Dict
    anomalies_detected: List[Dict]
    parsed_events: List[Dict]
    root_cause: Optional[Dict]
    repair_plan: List[Dict]
    reasoning_chain: List[Dict]
    current_agent: str
    status: str
    error: Optional[str]


class DataCollectorAgent:
    def __init__(self):
        self.name = "数据采集Agent"

    def collect_syslog(self, duration_seconds: int = 10) -> List[SyslogEntry]:
        from .simulator import SyslogSimulator
        simulator = SyslogSimulator()
        return simulator.generate_logs(count=duration_seconds)

    def collect_snmp(self, devices: List[str]) -> List[SNMPMetric]:
        from .simulator import SNMPSimulator
        simulator = SNMPSimulator()
        return simulator.generate_metrics(devices)

    def execute(self, state: AgentState) -> AgentState:
        state["current_agent"] = self.name
        state["step"] = 1

        logs = self.collect_syslog()
        metrics = self.collect_snmp(["core-01", "dist-01", "dist-02", "acc-01", "acc-02"])

        state["logs"] = [
            {
                "timestamp": log.timestamp,
                "source": log.source,
                "severity": log.severity,
                "message": log.message,
                "interface": log.interface
            }
            for log in logs
        ]

        state["metrics"] = [
            {
                "timestamp": m.get("timestamp"),
                "device": m.get("device"),
                "metric_name": m.get("metric_name"),
                "value": m.get("value"),
                "threshold": m.get("threshold")
            }
            for m in metrics
        ]

        state["data_collection_complete"] = True
        state["reasoning_chain"].append({
            "step": 1,
            "agent": self.name,
            "action": "数据采集完成",
            "status": "completed",
            "details": [
                f"采集Syslog: {len(logs)} 条",
                f"采集SNMP指标: {len(metrics)} 条",
                f"数据来源: 网络设备"
            ]
        })

        return state


class LogParserAgent:
    def __init__(self):
        self.name = "日志解析Agent"

    def parse_syslog(self, logs: List[Dict]) -> List[Dict]:
        parsed = []
        for log in logs:
            parsed_event = {
                "timestamp": log["timestamp"],
                "device": log["source"],
                "type": self._classify_log(log["message"]),
                "severity": log["severity"],
                "details": self._extract_details(log["message"])
            }
            parsed.append(parsed_event)
        return parsed

    def parse_snmp(self, metrics: List[Dict]) -> List[Dict]:
        parsed = []
        for metric in metrics:
            if metric["threshold"] and metric["value"] > metric["threshold"]:
                parsed.append({
                    "timestamp": metric["timestamp"],
                    "device": metric["device"],
                    "type": "threshold_exceeded",
                    "metric": metric["metric_name"],
                    "value": metric["value"],
                    "threshold": metric["threshold"],
                    "severity": "warning"
                })
        return parsed

    def _classify_log(self, message: str) -> str:
        message_lower = message.lower()
        if "crc error" in message_lower or "collision" in message_lower:
            return "physical_error"
        elif "down" in message_lower or "failed" in message_lower:
            return "link_down"
        elif "high" in message_lower or "exceeded" in message_lower:
            return "performance_warning"
        elif "change" in message_lower:
            return "config_change"
        return "general"

    def _extract_details(self, message: str) -> Dict:
        details = {"raw": message}
        if "interface" in message.lower():
            parts = message.split()
            for i, part in enumerate(parts):
                if "interface" in part.lower() and i + 1 < len(parts):
                    details["interface"] = parts[i + 1]
        return details

    def execute(self, state: AgentState) -> AgentState:
        state["current_agent"] = self.name
        state["step"] = 2

        parsed_logs = self.parse_syslog(state["logs"])
        parsed_metrics = self.parse_snmp(state["metrics"])

        state["parsed_events"] = parsed_logs + parsed_metrics

        anomalies = [e for e in state["parsed_events"] if e.get("severity") in ["error", "warning"]]
        state["anomalies_detected"] = anomalies

        state["reasoning_chain"].append({
            "step": 2,
            "agent": self.name,
            "action": "日志解析完成",
            "status": "completed",
            "details": [
                f"解析事件: {len(state['parsed_events'])} 条",
                f"检测异常: {len(anomalies)} 条",
                f"主要类型: {self._get_top_anomaly_types(anomalies)}"
            ]
        })

        return state

    def _get_top_anomaly_types(self, anomalies: List[Dict]) -> str:
        types = {}
        for a in anomalies:
            t = a.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
        return ", ".join([f"{k}({v})" for k, v in sorted(types.items(), key=lambda x: -x[1])[:3]])


class TopologyAgent:
    def __init__(self):
        self.name = "拓扑感知Agent"

    def get_topology(self) -> Dict:
        from .simulator import TopologySimulator
        topo = TopologySimulator()
        return topo.get_topology()

    def find_affected_path(self, topology: Dict, faulty_node: str) -> List[str]:
        path = [faulty_node]
        for link in topology.get("links", []):
            if link["source"] == faulty_node:
                path.append(link["target"])
            elif link["target"] == faulty_node:
                path.append(link["source"])
        return path

    def execute(self, state: AgentState) -> AgentState:
        state["current_agent"] = self.name
        state["step"] = 3

        topology = self.get_topology()
        state["topology"] = topology

        state["reasoning_chain"].append({
            "step": 3,
            "agent": self.name,
            "action": "拓扑分析完成",
            "status": "completed",
            "details": [
                f"节点数: {len(topology['nodes'])}",
                f"链路数: {len(topology['links'])}",
                f"网络层级: 核心-汇聚-接入"
            ]
        })

        return state


class ReasoningAgent:
    def __init__(self):
        self.name = "推理Agent"

    def analyze_root_cause(self, state: AgentState) -> RootCause:
        anomalies = state["anomalies_detected"]

        physical_errors = [a for a in anomalies if a.get("type") == "physical_error"]
        if physical_errors:
            primary_error = physical_errors[0]
            device = primary_error.get("device", "acc-02")
            details = primary_error.get("details", {})
            interface = details.get("interface", "GigabitEthernet0/1")

            evidence = [
                FaultEvidence(
                    type="syslog",
                    content=f"{interface}: CRC errors increased significantly",
                    timestamp=primary_error["timestamp"],
                    device=device,
                    confidence=0.95
                )
            ]

            for a in anomalies[:3]:
                if a.get("metric"):
                    evidence.append(FaultEvidence(
                        type="snmp",
                        content=f"{a['metric']}: {a['value']} (threshold: {a['threshold']})",
                        timestamp=a["timestamp"],
                        device=a["device"],
                        confidence=0.90
                    ))

            device_names = {
                "acc-02": "接入交换机-2",
                "dist-01": "汇聚交换机-A",
                "dist-02": "汇聚交换机-B",
                "core-01": "核心交换机"
            }

            return RootCause(
                device=device,
                device_name=device_names.get(device, device),
                port=interface,
                issue="端口物理损坏导致CRC错误率异常",
                confidence=0.92,
                evidence_chain=evidence
            )

        return RootCause(
            device="unknown",
            device_name="未知",
            port=None,
            issue="未检测到明显故障",
            confidence=0.0,
            evidence_chain=[]
        )

    def generate_repair_plan(self, root_cause: RootCause) -> List[RepairAction]:
        plan = [
            RepairAction(
                id=1,
                action="端口重启",
                command=f"interface {root_cause.port}\nshutdown\nno shutdown",
                description="重启故障端口以尝试恢复正常",
                auto_execute=True,
                status="pending"
            ),
            RepairAction(
                id=2,
                action="端口隔离",
                command=f"interface {root_cause.port}\nswitchport port-security maximum 0\nshutdown",
                description="禁用问题端口防止影响网络",
                auto_execute=False,
                status="pending"
            ),
            RepairAction(
                id=3,
                action="硬件更换",
                command="REPLACE HARDWARE",
                description="更换故障网线或模块",
                auto_execute=False,
                status="pending"
            )
        ]
        return plan

    def execute(self, state: AgentState) -> AgentState:
        state["current_agent"] = self.name
        state["step"] = 4

        root_cause = self.analyze_root_cause(state)

        state["root_cause"] = {
            "device": root_cause.device,
            "device_name": root_cause.device_name,
            "port": root_cause.port,
            "issue": root_cause.issue,
            "confidence": root_cause.confidence,
            "evidence": [
                {
                    "type": e.type,
                    "content": e.content,
                    "timestamp": e.timestamp,
                    "device": e.device
                }
                for e in root_cause.evidence_chain
            ]
        }

        repair_plan = self.generate_repair_plan(root_cause)
        state["repair_plan"] = [
            {
                "id": a.id,
                "action": a.action,
                "command": a.command,
                "description": a.description,
                "auto_execute": a.auto_execute,
                "status": a.status
            }
            for a in repair_plan
        ]

        state["reasoning_chain"].append({
            "step": 4,
            "agent": self.name,
            "action": "根因分析完成",
            "status": "completed",
            "details": [
                f"故障类型: {root_cause.issue}",
                f"根因设备: {root_cause.device_name}",
                f"根因端口: {root_cause.port}",
                f"置信度: {root_cause.confidence * 100:.0f}%"
            ]
        })

        return state


class ExecutorAgent:
    def __init__(self):
        self.name = "执行Agent"

    def execute_command(self, command: str, device: str) -> Dict:
        return {
            "success": True,
            "command": command,
            "device": device,
            "output": "Command executed successfully",
            "timestamp": datetime.now().isoformat()
        }

    def execute(self, state: AgentState) -> AgentState:
        state["current_agent"] = self.name
        state["step"] = 5

        state["reasoning_chain"].append({
            "step": 5,
            "agent": self.name,
            "action": "修复方案生成",
            "status": "completed",
            "details": [
                f"待执行操作: {len(state['repair_plan'])} 项",
                f"自动执行: {len([p for p in state['repair_plan'] if p['auto_execute']])} 项",
                f"手动确认: {len([p for p in state['repair_plan'] if not p['auto_execute']])} 项"
            ]
        })

        state["status"] = "completed"

        return state
