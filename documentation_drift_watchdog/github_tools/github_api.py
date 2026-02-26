import os
import httpx
import logging

GITHUB_API_URL = "https://api.github.com"

class GitHubAPI:
    def __init__(self, token, user_or_org):
        self.token = token
        self.user_or_org = user_or_org
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }

    async def get_repos(self):
        url = f"{GITHUB_API_URL}/users/{self.user_or_org}/repos?per_page=100"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return [repo['name'] for repo in resp.json()]

    async def get_repo_commits(self, repo, branch="main", since=None):
        url = f"{GITHUB_API_URL}/repos/{self.user_or_org}/{repo}/commits?sha={branch}"
        if since:
            url += f"&since={since}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_commit_diff(self, repo, sha):
        url = f"{GITHUB_API_URL}/repos/{self.user_or_org}/{repo}/commits/{sha}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def create_pull_request(self, repo, branch, base, title, body):
        url = f"{GITHUB_API_URL}/repos/{self.user_or_org}/{repo}/pulls"
        data = {
            "title": title,
            "head": branch,
            "base": base,
            "body": body
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self.headers, json=data)
            resp.raise_for_status()
            return resp.json()
