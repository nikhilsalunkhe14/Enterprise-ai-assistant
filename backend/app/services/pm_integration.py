import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from app.core.logger import logger
from app.core.config import settings

class PMToolIntegration:
    """Integration with popular Project Management tools"""
    
    def __init__(self):
        self.jira_token = getattr(settings, 'JIRA_TOKEN', None)
        self.trello_key = getattr(settings, 'TRELLO_KEY', None)
        self.trello_token = getattr(settings, 'TRELLO_TOKEN', None)
        self.asana_token = getattr(settings, 'ASANA_TOKEN', None)
        
    async def get_jira_projects(self) -> List[Dict]:
        """Get projects from Jira"""
        if not self.jira_token:
            return []
        
        try:
            url = "https://your-domain.atlassian.net/rest/api/3/project"
            headers = {
                "Authorization": f"Bearer {self.jira_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        projects = await response.json()
                        return self._format_jira_projects(projects)
                    else:
                        logger.error(f"Jira API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Jira integration error: {str(e)}")
            return []
    
    async def get_trello_boards(self) -> List[Dict]:
        """Get boards from Trello"""
        if not self.trello_key or not self.trello_token:
            return []
        
        try:
            url = f"https://api.trello.com/1/members/me/boards?key={self.trello_key}&token={self.trello_token}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        boards = await response.json()
                        return self._format_trello_boards(boards)
                    else:
                        logger.error(f"Trello API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Trello integration error: {str(e)}")
            return []
    
    async def get_asana_projects(self) -> List[Dict]:
        """Get projects from Asana"""
        if not self.asana_token:
            return []
        
        try:
            url = "https://app.asana.com/api/1.0/projects"
            headers = {
                "Authorization": f"Bearer {self.asana_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        projects = await response.json()
                        return self._format_asana_projects(projects)
                    else:
                        logger.error(f"Asana API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Asana integration error: {str(e)}")
            return []
    
    async def create_jira_task(self, project_key: str, summary: str, description: str) -> Optional[Dict]:
        """Create a task in Jira"""
        if not self.jira_token:
            return None
        
        try:
            url = f"https://your-domain.atlassian.net/rest/api/3/issue"
            headers = {
                "Authorization": f"Bearer {self.jira_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{
                                "type": "text",
                                "text": description
                            }]
                        }]
                    },
                    "issuetype": {"name": "Task"}
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 201:
                        task = await response.json()
                        return {
                            "id": task["id"],
                            "key": task["key"],
                            "url": f"https://your-domain.atlassian.net/browse/{task['key']}"
                        }
                    else:
                        logger.error(f"Jira task creation error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Jira task creation error: {str(e)}")
            return None
    
    async def create_trello_card(self, board_id: str, list_id: str, name: str, desc: str) -> Optional[Dict]:
        """Create a card in Trello"""
        if not self.trello_key or not self.trello_token:
            return None
        
        try:
            url = f"https://api.trello.com/1/cards"
            params = {
                "key": self.trello_key,
                "token": self.trello_token,
                "idList": list_id,
                "name": name,
                "desc": desc
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params) as response:
                    if response.status == 200:
                        card = await response.json()
                        return {
                            "id": card["id"],
                            "name": card["name"],
                            "url": card["url"]
                        }
                    else:
                        logger.error(f"Trello card creation error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Trello card creation error: {str(e)}")
            return None
    
    async def get_project_data(self, tool: str, project_id: str) -> Dict:
        """Get project data from specified tool"""
        if tool.lower() == "jira":
            return await self._get_jira_project_data(project_id)
        elif tool.lower() == "trello":
            return await self._get_trello_board_data(project_id)
        elif tool.lower() == "asana":
            return await self._get_asana_project_data(project_id)
        else:
            return {"error": f"Unsupported tool: {tool}"}
    
    def _format_jira_projects(self, projects: List[Dict]) -> List[Dict]:
        return [{
            "id": project["id"],
            "key": project["key"],
            "name": project["name"],
            "tool": "Jira",
            "url": f"https://your-domain.atlassian.net/browse/{project['key']}"
        } for project in projects]
    
    def _format_trello_boards(self, boards: List[Dict]) -> List[Dict]:
        return [{
            "id": board["id"],
            "name": board["name"],
            "tool": "Trello",
            "url": board["url"]
        } for board in boards]
    
    def _format_asana_projects(self, projects: Dict) -> List[Dict]:
        return [{
            "id": project["gid"],
            "name": project["name"],
            "tool": "Asana",
            "url": f"https://app.asana.com/0/{project['gid']}"
        } for project in projects.get("data", [])]
    
    async def _get_jira_project_data(self, project_key: str) -> Dict:
        """Get detailed project data from Jira"""
        # Implementation for Jira project data
        return {"tool": "Jira", "project_key": project_key, "data": "mock_data"}
    
    async def _get_trello_board_data(self, board_id: str) -> Dict:
        """Get detailed board data from Trello"""
        # Implementation for Trello board data
        return {"tool": "Trello", "board_id": board_id, "data": "mock_data"}
    
    async def _get_asana_project_data(self, project_id: str) -> Dict:
        """Get detailed project data from Asana"""
        # Implementation for Asana project data
        return {"tool": "Asana", "project_id": project_id, "data": "mock_data"}
    
    async def sync_all_projects(self) -> Dict:
        """Sync projects from all integrated tools"""
        tasks = []
        
        if self.jira_token:
            tasks.append(self.get_jira_projects())
        if self.trello_key and self.trello_token:
            tasks.append(self.get_trello_boards())
        if self.asana_token:
            tasks.append(self.get_asana_projects())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_projects = []
        for result in results:
            if isinstance(result, list):
                all_projects.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Project sync error: {str(result)}")
        
        return {
            "projects": all_projects,
            "total_count": len(all_projects),
            "tools_connected": sum(1 for token in [self.jira_token, self.trello_key, self.asana_token] if token)
        }
