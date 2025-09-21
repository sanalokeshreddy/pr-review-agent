import requests
import tempfile
import os
import subprocess
from urllib.parse import urlparse
from config import Config

class GitUtils:
    @staticmethod
    def parse_git_url(url):
        """Parse git repository URL to determine provider and extract details"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if 'github.com' in parsed.netloc:
            if len(path_parts) >= 4 and path_parts[2] == 'pull':
                return {
                    'provider': 'github',
                    'owner': path_parts[0],
                    'repo': path_parts[1],
                    'pr_number': path_parts[3]
                }
        elif 'gitlab.com' in parsed.netloc:
            # GitLab MR URLs have different formats
            if 'merge_requests' in path_parts:
                mr_index = path_parts.index('merge_requests')
                return {
                    'provider': 'gitlab',
                    'project_path': '/'.join(path_parts[:mr_index]),
                    'mr_number': path_parts[mr_index + 1]
                }
        elif 'bitbucket.org' in parsed.netloc:
            if 'pull-requests' in path_parts:
                pr_index = path_parts.index('pull-requests')
                return {
                    'provider': 'bitbucket',
                    'owner': path_parts[0],
                    'repo': path_parts[1],
                    'pr_number': path_parts[pr_index + 1]
                }
        
        return {'provider': 'unknown'}
    
    @staticmethod
    def get_pr_details(pr_url):
        """Get PR details from various git providers"""
        parsed = GitUtils.parse_git_url(pr_url)
        provider = parsed.get('provider')
        
        if provider == 'github':
            return GitUtils._get_github_pr_details(parsed)
        elif provider == 'gitlab':
            return GitUtils._get_gitlab_pr_details(parsed)
        elif provider == 'bitbucket':
            return GitUtils._get_bitbucket_pr_details(parsed)
        else:
            return {"error": "Unsupported git provider or invalid URL"}
    
    @staticmethod
    def _get_github_pr_details(parsed):
        """Get PR details from GitHub"""
        owner = parsed.get('owner')
        repo = parsed.get('repo')
        pr_number = parsed.get('pr_number')
        
        if not all([owner, repo, pr_number]):
            return {"error": "Invalid GitHub PR URL format"}
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'PR-Review-Agent'
        }
        
        if Config.GITHUB_TOKEN:
            headers['Authorization'] = f'token {Config.GITHUB_TOKEN}'
        
        api_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                pr_data = response.json()
                return {
                    'title': pr_data.get('title', ''),
                    'description': pr_data.get('body', ''),
                    'author': pr_data.get('user', {}).get('login', ''),
                    'state': pr_data.get('state', ''),
                    'created_at': pr_data.get('created_at', ''),
                    'updated_at': pr_data.get('updated_at', ''),
                    'base_branch': pr_data.get('base', {}).get('ref', ''),
                    'head_branch': pr_data.get('head', {}).get('ref', ''),
                    'provider': 'github'
                }
            elif response.status_code == 404:
                # Try to get basic info from the webpage for public repos
                return GitUtils._get_github_pr_basic_info(parsed)
            else:
                return {"error": f"Failed to fetch PR details: {response.status_code} - {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
    
    @staticmethod
    def _get_github_pr_basic_info(parsed):
        """Get basic PR info from GitHub when API fails"""
        owner = parsed.get('owner')
        repo = parsed.get('repo')
        pr_number = parsed.get('pr_number')
        
        return {
            'title': f"PR #{pr_number} from {owner}/{repo}",
            'description': 'Unable to fetch detailed description. Using direct diff analysis.',
            'author': 'Unknown',
            'state': 'unknown',
            'base_branch': 'main',
            'head_branch': 'feature',
            'provider': 'github',
            'note': 'Using basic info due to API limitations'
        }
    
    @staticmethod
    def _get_gitlab_pr_details(parsed):
        """Get PR (Merge Request) details from GitLab"""
        project_path = parsed.get('project_path')
        mr_number = parsed.get('mr_number')
        
        if not all([project_path, mr_number]):
            return {"error": "Invalid GitLab MR URL format"}
        
        headers = {}
        if Config.GITLAB_TOKEN:
            headers['PRIVATE-TOKEN'] = Config.GITLAB_TOKEN
        
        api_url = f'https://gitlab.com/api/v4/projects/{project_path.replace("/", "%2F")}/merge_requests/{mr_number}'
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                mr_data = response.json()
                return {
                    'title': mr_data.get('title', ''),
                    'description': mr_data.get('description', ''),
                    'author': mr_data.get('author', {}).get('username', ''),
                    'state': mr_data.get('state', ''),
                    'created_at': mr_data.get('created_at', ''),
                    'updated_at': mr_data.get('updated_at', ''),
                    'base_branch': mr_data.get('target_branch', ''),
                    'head_branch': mr_data.get('source_branch', ''),
                    'provider': 'gitlab'
                }
            else:
                return {"error": f"Failed to fetch MR details: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
    
    @staticmethod
    def _get_bitbucket_pr_details(parsed):
        """Get PR details from Bitbucket"""
        workspace = parsed.get('owner')
        repo_slug = parsed.get('repo')
        pr_id = parsed.get('pr_number')
        
        if not all([workspace, repo_slug, pr_id]):
            return {"error": "Invalid Bitbucket PR URL format"}
        
        auth = None
        if Config.BITBUCKET_USERNAME and Config.BITBUCKET_APP_PASSWORD:
            auth = (Config.BITBUCKET_USERNAME, Config.BITBUCKET_APP_PASSWORD)
        
        api_url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}'
        
        try:
            response = requests.get(api_url, auth=auth, timeout=10)
            
            if response.status_code == 200:
                pr_data = response.json()
                return {
                    'title': pr_data.get('title', ''),
                    'description': pr_data.get('description', {}).get('raw', ''),
                    'author': pr_data.get('author', {}).get('display_name', ''),
                    'state': pr_data.get('state', ''),
                    'created_at': pr_data.get('created_on', ''),
                    'updated_at': pr_data.get('updated_on', ''),
                    'base_branch': pr_data.get('destination', {}).get('branch', {}).get('name', ''),
                    'head_branch': pr_data.get('source', {}).get('branch', {}).get('name', ''),
                    'provider': 'bitbucket'
                }
            else:
                return {"error": f"Failed to fetch PR details: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
    
    @staticmethod
    def get_pr_diff(pr_url):
        """Get the diff for a PR from various git providers"""
        parsed = GitUtils.parse_git_url(pr_url)
        provider = parsed.get('provider')
        
        if provider == 'github':
            return GitUtils._get_github_pr_diff(parsed)
        elif provider == 'gitlab':
            return GitUtils._get_gitlab_pr_diff(parsed)
        elif provider == 'bitbucket':
            return GitUtils._get_bitbucket_pr_diff(parsed)
        else:
            return {"error": "Unsupported git provider or invalid URL"}
    
    @staticmethod
    def _get_github_pr_diff(parsed):
        """Get PR diff from GitHub"""
        owner = parsed.get('owner')
        repo = parsed.get('repo')
        pr_number = parsed.get('pr_number')
        
        if not all([owner, repo, pr_number]):
            return "Error: Invalid GitHub PR URL format"
        
        # Try to get diff directly from GitHub's raw endpoint
        diff_url = f'https://patch-diff.githubusercontent.com/raw/{owner}/{repo}/pull/{pr_number}.diff'
        
        try:
            response = requests.get(diff_url, timeout=10)
            
            if response.status_code == 200:
                return response.text
            else:
                return f"Error: Failed to fetch diff - {response.status_code}. Using alternative method."
        except requests.exceptions.RequestException as e:
            return f"Error: Network issue - {str(e)}"
    
    @staticmethod
    def _get_gitlab_pr_diff(parsed):
        """Get MR diff from GitLab"""
        project_path = parsed.get('project_path')
        mr_number = parsed.get('mr_number')
        
        if not all([project_path, mr_number]):
            return "Error: Invalid GitLab MR URL format"
        
        # GitLab provides diff in their API response
        headers = {}
        if Config.GITLAB_TOKEN:
            headers['PRIVATE-TOKEN'] = Config.GITLAB_TOKEN
        
        api_url = f'https://gitlab.com/api/v4/projects/{project_path.replace("/", "%2F")}/merge_requests/{mr_number}/changes'
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                changes_data = response.json()
                diff_output = ""
                for change in changes_data.get('changes', []):
                    diff_output += f"--- a/{change['old_path']}\n"
                    diff_output += f"+++ b/{change['new_path']}\n"
                    diff_output += change['diff'] + "\n\n"
                return diff_output
            else:
                return f"Error: Failed to fetch diff - {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"Error: Network issue - {str(e)}"
    
    @staticmethod
    def _get_bitbucket_pr_diff(parsed):
        """Get PR diff from Bitbucket"""
        workspace = parsed.get('owner')
        repo_slug = parsed.get('repo')
        pr_id = parsed.get('pr_number')
        
        if not all([workspace, repo_slug, pr_id]):
            return "Error: Invalid Bitbucket PR URL format"
        
        auth = None
        if Config.BITBUCKET_USERNAME and Config.BITBUCKET_APP_PASSWORD:
            auth = (Config.BITBUCKET_USERNAME, Config.BITBUCKET_APP_PASSWORD)
        
        api_url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/diff'
        
        try:
            response = requests.get(api_url, auth=auth, timeout=10)
            
            if response.status_code == 200:
                return response.text
            else:
                return f"Error: Failed to fetch diff - {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"Error: Network issue - {str(e)}"