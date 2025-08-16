#!/usr/bin/env python3
"""
Check current workflow status
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_workflow_status():
    """Check current workflow status"""
    try:
        logger.info("🔍 Checking workflow status...")
        
        # Create system
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ System started")
        
        # Check if coordinator is available
        if system.coordinator:
            logger.info("✅ Coordinator is available")
            
            # Check active workflows
            active_workflows = getattr(system.coordinator, 'active_workflows', {})
            logger.info(f"📊 Active workflows: {list(active_workflows.keys())}")
            
            if active_workflows:
                for workflow_id, workflow in active_workflows.items():
                    logger.info(f"📋 Workflow {workflow_id}:")
                    logger.info(f"   Topic: {workflow.topic}")
                    logger.info(f"   Status: {workflow.overall_status}")
                    logger.info(f"   Current stage: {workflow.current_stage}")
                    logger.info(f"   Stages: {[stage.stage_name for stage in workflow.stages]}")
                    
                    if workflow.stages:
                        current_stage = workflow.stages[workflow.current_stage]
                        logger.info(f"   Current stage status: {current_stage.status}")
                        logger.info(f"   Current stage agent: {current_stage.agent_name}")
            else:
                logger.info("📊 No active workflows found")
        else:
            logger.error("❌ Coordinator not available")
        
        # Stop system
        await system.stop()
        logger.info("✅ System stopped")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_workflow_status())