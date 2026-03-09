from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/tools", tags=["tools"])

class JiraTicket(BaseModel):
    id: str
    title: str
    status: str
    priority: str

class TrelloBoard(BaseModel):
    id: str
    name: str
    tasks_count: int

@router.get("/jira/tickets", response_model=List[JiraTicket])
async def get_mock_jira_tickets():
    """Mock integration: Fetch active Jira tickets for the current sprint"""
    return [
        {"id": "PROJ-101", "title": "Setup Authentication", "status": "In Progress", "priority": "High"},
        {"id": "PROJ-102", "title": "Database Schema Migration", "status": "To Do", "priority": "Medium"},
        {"id": "PROJ-103", "title": "Implement Web Speech UI", "status": "Done", "priority": "Low"}
    ]

@router.get("/trello/boards", response_model=List[TrelloBoard])
async def get_mock_trello_boards():
    """Mock integration: Fetch Trello Board stats"""
    return [
        {"id": "board-A", "name": "Sprint 3 Deliverables", "tasks_count": 12},
        {"id": "board-B", "name": "Backlog", "tasks_count": 45}
    ]
