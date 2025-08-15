import asyncio
import os
import time

from patent_agent_demo.patent_agent_system import PatentAgentSystem


async def run_once():
	# Read topic and description from env or defaults
	topic = os.environ.get("PATENT_TOPIC", "证据图增强的检索增强RAG系统")
	description = os.environ.get(
		"PATENT_DESC",
		"一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统"
	)

	system = PatentAgentSystem()
	await system.start()

	# Start a new workflow via coordinator to avoid 300s wait in system API
	start = await system.coordinator.execute_task({
		"type": "start_patent_workflow",
		"topic": topic,
		"description": description,
		"workflow_type": "standard"
	})
	if not start.success:
		print(f"Failed to start workflow: {start.error_message}")
		await system.stop()
		return 2
	workflow_id = start.data.get("workflow_id")
	print(f"Started workflow: {workflow_id}")

	# Poll until completion (max 2 hours)
	start_time = time.time()
	max_wait = 7200
	exported_path = None
	while True:
		status = await system.coordinator.execute_task({
			"type": "monitor_workflow",
			"workflow_id": workflow_id
		})
		if status.success:
			wf = status.data.get("workflow")
			overall_status = None
			if hasattr(wf, "overall_status"):
				overall_status = getattr(wf, "overall_status", None)
			elif isinstance(wf, dict):
				overall_status = wf.get("overall_status")
			if overall_status == "completed":
				# Build expected export path (Coordinator writes it on completion)
				topic_str = getattr(wf, "topic", None) or (isinstance(wf, dict) and wf.get("topic")) or "patent"
				exported_path = f"/output/{topic_str.replace(' ', '_')}_{workflow_id[:8]}.md"
				print(f"Completed. Exported to: {exported_path}")
				break
		elapsed = time.time() - start_time
		if elapsed > max_wait:
			print("Timeout waiting for completion (7200s). You may continue to monitor logs or increase the limit.")
			break
		await asyncio.sleep(5)

	await system.stop()
	return 0


if __name__ == "__main__":
	asyncio.run(run_once())