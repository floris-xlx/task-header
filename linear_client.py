"""
Linear API client for interacting with Linear's GraphQL API.
"""

import requests
from typing import List, Dict, Any, Optional


class LinearClient:
    """Client for interacting with Linear's GraphQL API."""
    
    API_URL = "https://api.linear.app/graphql"
    
    def __init__(self, api_key: str):
        """
        Initialize Linear client.
        
        Args:
            api_key: Linear API key
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Optional query variables
            
        Returns:
            Query response data
            
        Raises:
            Exception: If request fails
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(
            self.API_URL,
            json=payload,
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Linear API request failed: {response.status_code} - {response.text}")
        
        data = response.json()
        
        if "errors" in data:
            raise Exception(f"Linear API error: {data['errors']}")
        
        return data.get("data", {})
    
    def get_viewer(self) -> Dict[str, Any]:
        """Get information about the authenticated user."""
        query = """
        query {
            viewer {
                id
                name
                email
            }
        }
        """
        return self._execute_query(query).get("viewer", {})
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams the user has access to."""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                    description
                }
            }
        }
        """
        result = self._execute_query(query)
        return result.get("teams", {}).get("nodes", [])
    
    def get_team_projects(self, team_id: str) -> List[Dict[str, Any]]:
        """
        Get projects for a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of projects
        """
        query = """
        query ($teamId: String!) {
            team(id: $teamId) {
                projects {
                    nodes {
                        id
                        name
                        description
                        state
                        progress
                    }
                }
            }
        }
        """
        result = self._execute_query(query, {"teamId": team_id})
        return result.get("team", {}).get("projects", {}).get("nodes", [])
    
    def get_team_issues(self, team_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get issues for a specific team.
        
        Args:
            team_id: Team ID
            limit: Maximum number of issues to return
            
        Returns:
            List of issues
        """
        query = """
        query ($teamId: String!, $first: Int!) {
            team(id: $teamId) {
                issues(first: $first, orderBy: updatedAt) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        state {
                            id
                            name
                            type
                        }
                        assignee {
                            id
                            name
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        result = self._execute_query(query, {"teamId": team_id, "first": limit})
        return result.get("team", {}).get("issues", {}).get("nodes", [])
    
    def get_project_issues(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get issues for a specific project.
        
        Args:
            project_id: Project ID
            limit: Maximum number of issues to return
            
        Returns:
            List of issues
        """
        query = """
        query ($projectId: String!, $first: Int!) {
            project(id: $projectId) {
                issues(first: $first, orderBy: updatedAt) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        state {
                            id
                            name
                            type
                        }
                        assignee {
                            id
                            name
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        result = self._execute_query(query, {"projectId": project_id, "first": limit})
        return result.get("project", {}).get("issues", {}).get("nodes", [])
    
    def get_my_issues(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get issues assigned to the current user.
        
        Args:
            limit: Maximum number of issues to return
            
        Returns:
            List of issues
        """
        query = """
        query ($first: Int!) {
            viewer {
                assignedIssues(first: $first, orderBy: updatedAt) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        state {
                            id
                            name
                            type
                        }
                        team {
                            id
                            name
                            key
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        result = self._execute_query(query, {"first": limit})
        return result.get("viewer", {}).get("assignedIssues", {}).get("nodes", [])
    
    def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """
        Get details for a specific issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Issue details
        """
        query = """
        query ($issueId: String!) {
            issue(id: $issueId) {
                id
                identifier
                title
                description
                priority
                state {
                    id
                    name
                    type
                }
                assignee {
                    id
                    name
                }
                team {
                    id
                    name
                    key
                }
                project {
                    id
                    name
                }
                createdAt
                updatedAt
            }
        }
        """
        result = self._execute_query(query, {"issueId": issue_id})
        return result.get("issue", {})
    
    def get_workflow_states(self, team_id: str) -> List[Dict[str, Any]]:
        """
        Get workflow states for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of workflow states
        """
        query = """
        query ($teamId: String!) {
            team(id: $teamId) {
                states {
                    nodes {
                        id
                        name
                        type
                        color
                        position
                    }
                }
            }
        }
        """
        result = self._execute_query(query, {"teamId": team_id})
        return result.get("team", {}).get("states", {}).get("nodes", [])
    
    def update_issue_state(self, issue_id: str, state_id: str) -> Dict[str, Any]:
        """
        Update the state of an issue.
        
        Args:
            issue_id: Issue ID
            state_id: New state ID
            
        Returns:
            Updated issue details
        """
        mutation = """
        mutation ($issueId: String!, $stateId: String!) {
            issueUpdate(id: $issueId, input: { stateId: $stateId }) {
                success
                issue {
                    id
                    identifier
                    title
                    state {
                        id
                        name
                        type
                    }
                }
            }
        }
        """
        result = self._execute_query(mutation, {"issueId": issue_id, "stateId": state_id})
        return result.get("issueUpdate", {})
    
    def create_issue(self, team_id: str, title: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new issue.
        
        Args:
            team_id: Team ID
            title: Issue title
            description: Issue description
            
        Returns:
            Created issue details
        """
        mutation = """
        mutation ($teamId: String!, $title: String!, $description: String) {
            issueCreate(input: { teamId: $teamId, title: $title, description: $description }) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    state {
                        id
                        name
                        type
                    }
                }
            }
        }
        """
        result = self._execute_query(mutation, {
            "teamId": team_id,
            "title": title,
            "description": description
        })
        return result.get("issueCreate", {})

