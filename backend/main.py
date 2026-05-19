from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
from datetime import datetime

from agents.workflow import NetworkFaultAnalysisWorkflow
from agents.simulator import TopologySimulator, SyslogSimulator, SNMPSimulator

app = FastAPI(
    title="Network Fault Analysis API",
    description="网络故障根因定位与自愈 Agent 系统 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = NetworkFaultAnalysisWorkflow()
topology_sim = TopologySimulator()
syslog_sim = SyslogSimulator()
snmp_sim = SNMPSimulator()


class DetectionRequest(BaseModel):
    duration: int = 10
    devices: Optional[List[str]] = None


class ExecuteCommandRequest(BaseModel):
    command: str
    device: str


@app.get("/")
async def root():
    return {
        "message": "Network Fault Analysis API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/status")
async def get_status():
    return {
        "agents": [
            {"name": "数据采集Agent", "status": "active", "lastUpdate": datetime.now().isoformat(), "description": "收集网络日志和指标数据"},
            {"name": "日志解析Agent", "status": "active", "lastUpdate": datetime.now().isoformat(), "description": "解析syslog和SNMP信息"},
            {"name": "拓扑感知Agent", "status": "active", "lastUpdate": datetime.now().isoformat(), "description": "构建和维护网络拓扑"},
            {"name": "推理Agent", "status": "active", "lastUpdate": datetime.now().isoformat(), "description": "执行根因分析和推理"},
            {"name": "执行Agent", "status": "idle", "lastUpdate": datetime.now().isoformat(), "description": "执行自愈操作"}
        ],
        "topology": topology_sim.get_topology()
    }


@app.get("/api/topology")
async def get_topology():
    return topology_sim.get_topology()


@app.get("/api/logs")
async def get_logs(count: int = 20):
    logs = syslog_sim.generate_logs(count)
    return {
        "logs": [
            {
                "timestamp": log.timestamp,
                "source": log.source,
                "severity": log.severity,
                "message": log.message,
                "interface": log.interface
            }
            for log in logs
        ],
        "total": len(logs)
    }


@app.get("/api/metrics")
async def get_metrics(devices: Optional[str] = None):
    device_list = devices.split(",") if devices else None
    metrics = snmp_sim.generate_metrics(device_list)
    return {
        "metrics": metrics,
        "total": len(metrics)
    }


@app.post("/api/detect")
async def start_detection(request: DetectionRequest):
    result = workflow.analyze()
    return result


@app.post("/api/detect/stream")
async def start_detection_stream(request: DetectionRequest):
    async def event_generator():
        reasoning_chain = []

        steps = [
            {"agent": "数据采集Agent", "action": "正在采集网络日志和指标...", "duration": 1.5},
            {"agent": "日志解析Agent", "action": "正在解析syslog和SNMP数据...", "duration": 1.2},
            {"agent": "拓扑感知Agent", "action": "正在分析网络拓扑关联...", "duration": 1.0},
            {"agent": "推理Agent", "action": "正在执行根因推理...", "duration": 2.0},
            {"agent": "执行Agent", "action": "正在生成自愈方案...", "duration": 0.8}
        ]

        for i, step in enumerate(steps):
            await asyncio.sleep(step["duration"])

            step_result = {
                "step": i + 1,
                "agent": step["agent"],
                "action": step["action"],
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "progress": ((i + 1) / len(steps)) * 100
            }

            if i == 0:
                step_result["details"] = ["采集Syslog: 10条", "采集SNMP指标: 15条"]
            elif i == 1:
                step_result["details"] = ["解析事件: 8条", "检测异常: 3条"]
            elif i == 2:
                step_result["details"] = ["节点数: 10", "链路数: 10"]
            elif i == 3:
                step_result["details"] = [
                    "故障类型: 端口CRC错误",
                    "根因设备: 接入交换机-2",
                    "置信度: 92%"
                ]
            elif i == 4:
                step_result["details"] = ["待执行操作: 3项", "自动执行: 1项"]

            reasoning_chain.append(step_result)
            yield f"data: {json.dumps(step_result, ensure_ascii=False)}\n\n"

        final_result = workflow.analyze()
        final_result["reasoning_chain"] = reasoning_chain

        yield f"data: {json.dumps({'type': 'complete', 'result': final_result}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/execute")
async def execute_command(request: ExecuteCommandRequest):
    await asyncio.sleep(1.5)

    return {
        "success": True,
        "command": request.command,
        "device": request.device,
        "output": "Command executed successfully",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/reports")
async def get_reports():
    return {
        "reports": [
            {
                "id": 1,
                "title": "接入交换机端口故障分析报告",
                "date": "2024-01-15 10:30",
                "size": "1.2MB",
                "type": "fault",
                "author": "系统自动生成"
            },
            {
                "id": 2,
                "title": "核心网络健康检查周报",
                "date": "2024-01-14 08:00",
                "size": "2.5MB",
                "type": "health",
                "author": "运维团队"
            }
        ]
    }


@app.get("/api/knowledge")
async def get_knowledge_base():
    return {
        "knowledge": [
            {
                "id": 1,
                "title": "CRC错误故障排查指南",
                "category": "故障处理",
                "description": "详细说明CRC错误的常见原因和排查步骤"
            },
            {
                "id": 2,
                "title": "交换机端口基础知识",
                "category": "技术文档",
                "description": "交换机端口类型、速率和工作模式说明"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
