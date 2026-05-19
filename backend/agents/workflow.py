from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
import json

from .agents import (
    AgentState,
    DataCollectorAgent,
    LogParserAgent,
    TopologyAgent,
    ReasoningAgent,
    ExecutorAgent
)


class WorkflowGraph:
    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: List[tuple] = []
        self._build_workflow()

    def _build_workflow(self):
        self.nodes = {
            "data_collector": DataCollectorAgent().execute,
            "log_parser": LogParserAgent().execute,
            "topology": TopologyAgent().execute,
            "reasoning": ReasoningAgent().execute,
            "executor": ExecutorAgent().execute,
        }
        self.edges = [
            ("data_collector", "log_parser"),
            ("log_parser", "topology"),
            ("topology", "reasoning"),
            ("reasoning", "executor"),
        ]

    def compile(self) -> "CompiledWorkflow":
        return CompiledWorkflow(self.nodes, self.edges)


class CompiledWorkflow:
    def __init__(self, nodes: Dict, edges: List):
        self.nodes = nodes
        self.edges = edges

    def invoke(self, initial_state: AgentState) -> AgentState:
        state = initial_state.copy()

        execution_order = [
            "data_collector",
            "log_parser",
            "topology",
            "reasoning",
            "executor"
        ]

        for node_name in execution_order:
            if node_name in self.nodes:
                state = self.nodes[node_name](state)

        return state


class NetworkFaultAnalysisWorkflow:
    def __init__(self):
        self.graph = WorkflowGraph().compile()

    def analyze(self) -> Dict[str, Any]:
        initial_state: AgentState = {
            "step": 0,
            "data_collection_complete": False,
            "logs": [],
            "metrics": [],
            "topology": {},
            "anomalies_detected": [],
            "parsed_events": [],
            "root_cause": None,
            "repair_plan": [],
            "reasoning_chain": [],
            "current_agent": "",
            "status": "running",
            "error": None
        }

        result = self.graph.invoke(initial_state)

        return {
            "status": result["status"],
            "timestamp": datetime.now().isoformat(),
            "reasoning_chain": result["reasoning_chain"],
            "root_cause": result["root_cause"],
            "repair_plan": result["repair_plan"],
            "evidence": result["root_cause"].get("evidence", []) if result["root_cause"] else [],
            "summary": self._generate_summary(result)
        }

    def _generate_summary(self, result: AgentState) -> Dict:
        root_cause = result.get("root_cause")

        if root_cause:
            return {
                "detected": True,
                "fault_type": root_cause.get("issue", "Unknown"),
                "severity": "high" if root_cause.get("confidence", 0) > 0.8 else "medium",
                "device": root_cause.get("device"),
                "device_name": root_cause.get("device_name"),
                "port": root_cause.get("port"),
                "confidence": root_cause.get("confidence", 0),
                "anomalies_count": len(result.get("anomalies_detected", [])),
                "steps_completed": result.get("step", 0)
            }

        return {
            "detected": False,
            "message": "No fault detected",
            "steps_completed": result.get("step", 0)
        }


workflow = NetworkFaultAnalysisWorkflow()
