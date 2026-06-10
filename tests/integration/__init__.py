"""集成测试 — v0.9.0.0 集成测试基础设施.

跑端到端 / mock HTTP / 真 DB 流程, 覆盖单元测试无法触达的跨模块场景.

跑法:
  pytest tests/integration/ -v           跑全部集成测试
  pytest tests/ -v -m "not integration"  跳过集成测试
  pytest tests/ -v -m integration        只跑集成测试
"""
