#!/usr/bin/env python3
"""
GitHub MCP Client - Access GitHub repositories via Model Context Protocol
Pure Python implementation with environment variable support
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Optional, Dict, Any, List

# Try to import python-dotenv, install if not available
try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GitHubMCPClient:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.server_process = None
        
    async def start_server(self):
        """Start the GitHub MCP server"""
        env = os.environ.copy()
        env["GITHUB_PERSONAL_ACCESS_TOKEN"] = self.github_token
        
        try:
            self.server_process = await asyncio.create_subprocess_exec(
                "npx", "@modelcontextprotocol/server-github",
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print("GitHub MCP Server started successfully")
            
            # Wait a moment for server to initialize
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Error starting server: {e}")
            print("Make sure you have Node.js and npx installed")
            raise
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server"""
        if not self.server_process:
            await self.start_server()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json.encode())
            await self.server_process.stdin.drain()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    self.server_process.stdout.readline(),
                    timeout=10.0
                )
                response_text = response_line.decode().strip()
                
                if response_text:
                    response = json.loads(response_text)
                    return response
                else:
                    return {"error": {"message": "Empty response from server"}}
                    
            except asyncio.TimeoutError:
                return {"error": {"message": "Server response timeout"}}
                
        except Exception as e:
            return {"error": {"message": f"Request failed: {str(e)}"}}
    
    # Simplified methods using direct GitHub API calls instead of MCP
    # This is more reliable for testing
    
    def get_github_headers(self):
        """Get headers for GitHub API requests"""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-MCP-Client"
        }
    
    async def list_user_repositories(self, username: Optional[str] = None, get_all: bool = True) -> List[Dict]:
        """List repositories using direct GitHub API - fetch ALL repositories"""
        import aiohttp
        
        base_url = f"https://api.github.com/users/{username}/repos" if username else "https://api.github.com/user/repos"
        all_repos = []
        page = 1
        per_page = 100  # Maximum allowed per page
        
        try:
            async with aiohttp.ClientSession() as session:
                while True:
                    # Add pagination parameters
                    url = f"{base_url}?page={page}&per_page={per_page}&sort=updated"
                    
                    async with session.get(url, headers=self.get_github_headers()) as response:
                        if response.status == 200:
                            repos = await response.json()
                            
                            if not repos:  # No more repositories
                                break
                                
                            all_repos.extend(repos)
                            
                            # If we got less than per_page, we're done
                            if len(repos) < per_page:
                                break
                            
                            if not get_all and len(all_repos) >= 30:  # Just get first 30 if get_all is False
                                break
                                
                            page += 1
                            
                            # Add a small delay to be nice to the API
                            await asyncio.sleep(0.1)
                            
                        elif response.status == 403:
                            print(f"GitHub API Rate Limit Hit: {response.status}")
                            break
                        else:
                            print(f"GitHub API Error: {response.status}")
                            break
                            
            return all_repos
            
        except Exception as e:
            print(f"Error fetching repositories: {e}")
            return []
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.get_github_headers()) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Repository not found or access denied: {response.status}"}
        except Exception as e:
            return {"error": f"Error fetching repository: {e}"}
    
    async def get_repository_contents(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get repository contents"""
        import aiohttp
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.get_github_headers()) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return []
        except Exception as e:
            print(f"Error fetching contents: {e}")
            return []
    
    async def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """Get file content (decoded)"""
        import aiohttp
        import base64
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.get_github_headers()) as response:
                    if response.status == 200:
                        file_data = await response.json()
                        if file_data.get("encoding") == "base64":
                            content = base64.b64decode(file_data["content"]).decode('utf-8')
                            return content
                        else:
                            return file_data.get("content", "")
                    else:
                        return f"Error: Could not fetch file (status: {response.status})"
        except Exception as e:
            return f"Error fetching file: {e}"
    
    async def search_repositories(self, query: str) -> List[Dict]:
        """Search repositories"""
        import aiohttp
        
        url = f"https://api.github.com/search/repositories?q={query}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.get_github_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("items", [])
                    else:
                        return []
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    async def close(self):
        """Close the MCP server connection"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()

# Main example function
async def main():
    # Load GitHub credentials from environment variables
    github_token = os.getenv("GITHUB_PAT")
    default_owner = os.getenv("GITHUB_OWNER")
    default_repo = os.getenv("GITHUB_REPO")
    remote_mcp_url = os.getenv("REMOTE_MCP_URL")
    
    # Validate required environment variables
    if not github_token:
        print("❌ Error: GITHUB_PAT environment variable not set!")
        print("Please create a .env file with:")
        print("GITHUB_PAT=your_github_personal_access_token")
        print("GITHUB_OWNER=your_github_username")
        print("GITHUB_REPO=your_default_repository")
        return
    
    if not default_owner:
        print("⚠️  Warning: GITHUB_OWNER not set, will use authenticated user")
        default_owner = "your_username"  # This will be determined from API
    
    if not default_repo:
        print("⚠️  Warning: GITHUB_REPO not set, will use first repository found")
        default_repo = "default_repo"
    
    print(f"🔐 Using GitHub Owner: {default_owner}")
    print(f"📁 Default Repository: {default_repo}")
    if remote_mcp_url:
        print(f"🌐 Remote MCP URL: {remote_mcp_url}")
    print(f"🔑 GitHub Token: ...{github_token[-8:]}")  # Show only last 8 characters
    
    client = GitHubMCPClient(github_token)
    
    try:
        print("\n=== GitHub MCP Client Demo ===\n")
        
        # Test 1: List ALL your repositories
        print("🔍 Fetching ALL your repositories...")
        repos = await client.list_user_repositories(get_all=True)
        
        if repos:
            print(f"✅ Found {len(repos)} total repositories:")
            for i, repo in enumerate(repos[:10]):  # Show first 10
                # Safely handle None description
                description = repo.get('description') or 'No description'
                description_preview = description[:50] + "..." if len(description) > 50 else description
                
                print(f"  {i+1}. {repo['name']} - {description_preview}")
                print(f"     Language: {repo.get('language') or 'Unknown'} | Stars: {repo.get('stargazers_count', 0)} | Private: {repo.get('private', False)}")
            
            if len(repos) > 10:
                print(f"     ... and {len(repos) - 10} more repositories")
                
            # Show repository statistics
            print(f"\n📊 Repository Statistics:")
            languages = {}
            public_count = 0
            private_count = 0
            total_stars = 0
            
            for repo in repos:
                # Count languages
                lang = repo.get('language') or 'Unknown'
                languages[lang] = languages.get(lang, 0) + 1
                
                # Count public/private
                if repo.get('private'):
                    private_count += 1
                else:
                    public_count += 1
                
                # Count total stars
                total_stars += repo.get('stargazers_count', 0)
            
            print(f"  Total: {len(repos)} repositories")
            print(f"  Public: {public_count}, Private: {private_count}")
            print(f"  Total Stars: {total_stars}")
            
            # Show top languages
            sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            print(f"  Top Languages:")
            for lang, count in sorted_languages[:5]:
                print(f"    {lang}: {count} repos")
                
        else:
            print("❌ No repositories found or error occurred")
            return
        
        # Test 2: Get detailed info about your specific repo
        print(f"\n📋 Getting detailed info for: {default_owner}/{default_repo}")
        repo_info = await client.get_repository_info(default_owner, default_repo)
        
        if "error" not in repo_info:
            print(f"  Repository: {repo_info.get('full_name')}")
            print(f"  Description: {repo_info.get('description', 'No description')}")
            print(f"  Created: {repo_info.get('created_at', 'Unknown')[:10]}")
            print(f"  Last Updated: {repo_info.get('updated_at', 'Unknown')[:10]}")
            print(f"  Stars: {repo_info.get('stargazers_count', 0)}")
            print(f"  Forks: {repo_info.get('forks_count', 0)}")
            print(f"  Size: {repo_info.get('size', 0)} KB")
            print(f"  Language: {repo_info.get('language', 'Unknown')}")
            print(f"  Private: {repo_info.get('private', False)}")
        else:
            print(f"  Error: {repo_info['error']}")
        
        # Test 3: List your specific repository contents
        print(f"\n📁 Contents of {default_owner}/{default_repo}:")
        contents = await client.get_repository_contents(default_owner, default_repo)
        
        if contents:
            for item in contents:
                icon = "📁" if item['type'] == 'dir' else "📄"
                size_info = f" ({item.get('size', 0)} bytes)" if item['type'] == 'file' else ""
                print(f"  {icon} {item['name']}{size_info}")
        else:
            print("  No contents found or access denied")
        
        # Test 4: Try to get README content from your repo
        print(f"\n📖 README content from {default_owner}/{default_repo}:")
        readme_files = ['README.md', 'README.txt', 'README.rst', 'readme.md', 'README']
        readme_found = False
        
        for readme_file in readme_files:
            content = await client.get_file_content(default_owner, default_repo, readme_file)
            if not content.startswith("Error:"):
                print(f"  Found {readme_file}:")
                print(f"  {'-' * 40}")
                print(f"  {content[:500]}{'...' if len(content) > 500 else ''}")
                readme_found = True
                break
        
        if not readme_found:
            print("  No README file found")
        
        # Test 5: Show specific files from your repository
        print(f"\n📄 Looking for common files in {default_owner}/{default_repo}:")
        common_files = [
            'package.json', 'requirements.txt', 'setup.py', 'Dockerfile', 
            '.gitignore', 'LICENSE', 'config.py', 'main.py', 'index.js'
        ]
        
        for filename in common_files:
            content = await client.get_file_content(default_owner, default_repo, filename)
            if not content.startswith("Error:"):
                print(f"  ✅ Found: {filename} ({len(content)} characters)")
                # Show first few lines for code files
                if filename.endswith(('.py', '.js', '.json', '.yml', '.yaml')):
                    lines = content.split('\n')[:5]
                    print(f"     Preview: {lines[0][:60]}...")
        
        # Test 6: List directories in your repo
        if contents:
            directories = [item for item in contents if item['type'] == 'dir']
            if directories:
                print(f"\n📁 Exploring directories in {default_owner}/{default_repo}:")
                for directory in directories[:3]:  # Show first 3 directories
                    dir_name = directory['name']
                    print(f"  📁 {dir_name}/")
                    dir_contents = await client.get_repository_contents(default_owner, default_repo, dir_name)
                    if dir_contents:
                        for item in dir_contents[:5]:  # Show first 5 items in each directory
                            icon = "📁" if item['type'] == 'dir' else "📄"
                            print(f"    {icon} {item['name']}")
                        if len(dir_contents) > 5:
                            print(f"    ... and {len(dir_contents) - 5} more items")
        
        # Test 7: Search for your other repositories
        print(f"\n🔎 Searching for other repositories by {default_owner}...")
        search_results = await client.search_repositories(f"user:{default_owner}")
        
        if search_results:
            print(f"✅ Found {len(search_results)} repositories by {default_owner}:")
            for i, repo in enumerate(search_results):
                # Safely handle None description
                description = repo.get('description') or 'No description'
                description_preview = description[:60] + "..." if len(description) > 60 else description
                
                # Safely handle None language
                language = repo.get('language') or 'Unknown'
                
                print(f"  {i+1}. {repo['name']} ⭐ {repo['stargazers_count']}")
                print(f"     {description_preview}")
                print(f"     Language: {language} | Updated: {repo.get('updated_at', 'Unknown')[:10]}")
        else:
            print(f"No repositories found for {default_owner}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

# Interactive mode
async def interactive_mode():
    # Load GitHub credentials from environment variables
    github_token = os.getenv("GITHUB_PAT")
    default_owner = os.getenv("GITHUB_OWNER", "your_username")
    default_repo = os.getenv("GITHUB_REPO", "default_repo")
    
    # Validate required environment variables
    if not github_token:
        print("❌ Error: GITHUB_PAT environment variable not set!")
        print("Please create a .env file with your GitHub credentials")
        return
    
    print(f"🔐 Using GitHub Owner: {default_owner}")
    print(f"📁 Default Repository: {default_repo}")
    print(f"🔑 GitHub Token: ...{github_token[-8:]}")  # Show only last 8 characters
    
    client = GitHubMCPClient(github_token)
    
    while True:
        print("\n" + "="*50)
        print("GitHub MCP Client - Interactive Mode")
        print("1. List my repositories")
        print(f"2. Get repository info (default: {default_owner}/{default_repo})")
        print(f"3. Get file content (default: {default_owner}/{default_repo})")
        print("4. Search repositories")
        print(f"5. Explore {default_repo} repository structure")
        print("6. Exit")
        print("="*50)
        
        choice = input("Choose an option (1-6): ").strip()
        
        try:
            if choice == "1":
                print("Fetching ALL repositories...")
                repos = await client.list_user_repositories(get_all=True)
                if repos:
                    print(f"Found {len(repos)} total repositories (showing first 20):")
                    for i, repo in enumerate(repos[:20]):
                        description = repo.get('description') or 'No description'
                        lang = repo.get('language') or 'Unknown'
                        private_status = "🔒" if repo.get('private') else "🌐"
                        print(f"{i+1}. {private_status} {repo['name']} ({lang})")
                        print(f"    {description[:60]}...")
                    
                    if len(repos) > 20:
                        print(f"    ... and {len(repos) - 20} more repositories")
                        
                    # Quick stats
                    public = sum(1 for r in repos if not r.get('private'))
                    private = sum(1 for r in repos if r.get('private'))
                    total_stars = sum(r.get('stargazers_count', 0) for r in repos)
                    print(f"\n📊 Quick Stats: Public: {public}, Private: {private}, Total Stars: {total_stars}")
                else:
                    print("No repositories found")
            
            elif choice == "2":
                owner = input(f"Enter repository owner (default: {default_owner}): ").strip() or default_owner
                repo_name = input(f"Enter repository name (default: {default_repo}): ").strip() or default_repo
                info = await client.get_repository_info(owner, repo_name)
                if "error" not in info:
                    print(f"Name: {info.get('name')}")
                    print(f"Full Name: {info.get('full_name')}")
                    print(f"Description: {info.get('description', 'None')}")
                    print(f"Stars: {info.get('stargazers_count', 0)}")
                    print(f"Forks: {info.get('forks_count', 0)}")
                    print(f"Language: {info.get('language', 'Unknown')}")
                    print(f"Size: {info.get('size', 0)} KB")
                    print(f"Private: {info.get('private', False)}")
                    print(f"Created: {info.get('created_at', 'Unknown')[:10]}")
                    print(f"Updated: {info.get('updated_at', 'Unknown')[:10]}")
                else:
                    print(f"Error: {info['error']}")
            
            elif choice == "3":
                owner = input(f"Enter repository owner (default: {default_owner}): ").strip() or default_owner
                repo_name = input(f"Enter repository name (default: {default_repo}): ").strip() or default_repo
                file_path = input("Enter file path: ").strip()
                if file_path:
                    content = await client.get_file_content(owner, repo_name, file_path)
                    print("File content:")
                    print("-" * 40)
                    print(content[:1000] + ("..." if len(content) > 1000 else ""))
            
            elif choice == "4":
                query = input(f"Enter search query (try 'user:{default_owner}' for your repos): ").strip()
                if query:
                    results = await client.search_repositories(query)
                    if results:
                        print(f"Found {len(results)} results (showing first 10):")
                        for i, repo in enumerate(results[:10]):
                            # Safely handle None description
                            description = repo.get('description') or 'No description'
                            description_preview = description[:60] + "..." if len(description) > 60 else description
                            
                            print(f"{i+1}. {repo['full_name']} ⭐ {repo['stargazers_count']}")
                            print(f"   {description_preview}")
                    else:
                        print("No results found")
            
            elif choice == "5":
                print(f"🔍 Exploring {default_owner}/{default_repo} repository structure...")
                
                # Get main directory contents
                contents = await client.get_repository_contents(default_owner, default_repo)
                if contents:
                    print(f"\n📁 Root directory contents:")
                    directories = []
                    files = []
                    
                    for item in contents:
                        if item['type'] == 'dir':
                            directories.append(item)
                        else:
                            files.append(item)
                    
                    print("📁 Directories:")
                    for directory in directories:
                        print(f"  📁 {directory['name']}/")
                    
                    print("\n📄 Files:")
                    for file in files:
                        size = f" ({file.get('size', 0)} bytes)" if file.get('size') else ""
                        print(f"  📄 {file['name']}{size}")
                    
                    # Let user explore a directory
                    if directories:
                        dir_name = input(f"\nEnter directory name to explore (or press Enter to skip): ").strip()
                        if dir_name and any(d['name'] == dir_name for d in directories):
                            dir_contents = await client.get_repository_contents(default_owner, default_repo, dir_name)
                            if dir_contents:
                                print(f"\n📁 Contents of {dir_name}/:")
                                for item in dir_contents:
                                    icon = "📁" if item['type'] == 'dir' else "📄"
                                    size = f" ({item.get('size', 0)} bytes)" if item['type'] == 'file' and item.get('size') else ""
                                    print(f"  {icon} {item['name']}{size}")
                else:
                    print("Could not access repository contents")
            
            elif choice == "6":
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except Exception as e:
            print(f"Error: {e}")
    
    await client.close()
    print("Goodbye!")

# Check if required dependencies are installed
def check_dependencies():
    """Check and install required dependencies"""
    dependencies = [
        ("aiohttp", "aiohttp"),
        ("python-dotenv", "python-dotenv")
    ]
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name.replace("-", "_"))
        except ImportError:
            print(f"Installing required dependency: {package_name}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} installed successfully")

if __name__ == "__main__":
    check_dependencies()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())