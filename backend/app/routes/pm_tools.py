from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.enhanced_prompt_engine import EnhancedPromptEngine
from app.core.logger import logger

router = APIRouter(prefix="/api/pm-tools", tags=["Project Management Integration"])

# Initialize PM integration
pm_engine = EnhancedPromptEngine()

@router.get("/projects")
async def get_all_projects():
    """Get all projects from integrated PM tools"""
    try:
        result = await pm_engine.pm_integration.sync_all_projects()
        return {
            "success": True,
            "data": result,
            "message": f"Retrieved {result['total_count']} projects from {result['tools_connected']} tools"
        }
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch projects")

@router.get("/projects/{tool}")
async def get_projects_by_tool(tool: str):
    """Get projects from specific PM tool"""
    try:
        if tool.lower() == "jira":
            projects = await pm_engine.pm_integration.get_jira_projects()
        elif tool.lower() == "trello":
            projects = await pm_engine.pm_integration.get_trello_boards()
        elif tool.lower() == "asana":
            projects = await pm_engine.pm_integration.get_asana_projects()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported tool: {tool}")
        
        return {
            "success": True,
            "data": projects,
            "message": f"Retrieved {len(projects)} projects from {tool}"
        }
    except Exception as e:
        logger.error(f"Error fetching {tool} projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch {tool} projects")

@router.post("/tasks/jira")
async def create_jira_task(project_key: str, summary: str, description: str):
    """Create a task in Jira"""
    try:
        task = await pm_engine.pm_integration.create_jira_task(project_key, summary, description)
        if task:
            return {
                "success": True,
                "data": task,
                "message": "Jira task created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create Jira task")
    except Exception as e:
        logger.error(f"Error creating Jira task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create Jira task")

@router.post("/tasks/trello")
async def create_trello_card(board_id: str, list_id: str, name: str, desc: str):
    """Create a card in Trello"""
    try:
        card = await pm_engine.pm_integration.create_trello_card(board_id, list_id, name, desc)
        if card:
            return {
                "success": True,
                "data": card,
                "message": "Trello card created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create Trello card")
    except Exception as e:
        logger.error(f"Error creating Trello card: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create Trello card")

@router.get("/project-data/{tool}/{project_id}")
async def get_project_data(tool: str, project_id: str):
    """Get detailed project data from PM tool"""
    try:
        data = await pm_engine.pm_integration.get_project_data(tool, project_id)
        return {
            "success": True,
            "data": data,
            "message": f"Retrieved project data from {tool}"
        }
    except Exception as e:
        logger.error(f"Error fetching project data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch project data")

@router.get("/status")
async def get_integration_status():
    """Get PM tool integration status"""
    try:
        status = {
            "jira": bool(pm_engine.pm_integration.jira_token),
            "trello": bool(pm_engine.pm_integration.trello_key and pm_engine.pm_integration.trello_token),
            "asana": bool(pm_engine.pm_integration.asana_token),
            "total_connected": sum([
                bool(pm_engine.pm_integration.jira_token),
                bool(pm_engine.pm_integration.trello_key and pm_engine.pm_integration.trello_token),
                bool(pm_engine.pm_integration.asana_token)
            ])
        }
        
        return {
            "success": True,
            "data": status,
            "message": f"Connected to {status['total_connected']}/3 PM tools"
        }
    except Exception as e:
        logger.error(f"Error checking integration status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check integration status")
