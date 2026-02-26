import asyncio
from langgraph.graph import StateGraph, END
from github_tools.github_api import GitHubAPI
from github_tools.git_diff import GitDiffExtractor
from core.semantic_change import extract_python_changes
from agents.reasoning_agent import ReasoningAgent
from core.doc_editor import DocumentationEditor
from core.pr_creator import create_drift_pr
from memory.drift_memory import DriftMemory
import os

async def run_workflow(event, config):
    # Setup
    gh = GitHubAPI(config['GITHUB_TOKEN'], config['GITHUB_USER_OR_ORG'])
    memory = DriftMemory(config['MEMORY_DB_PATH'])
    doc_editor = DocumentationEditor()
    agent = ReasoningAgent(config)

    # Discover repositories
    if event['scan_mode'] == 'all':
        repos = await gh.get_repos()
    elif event['scan_mode'] == 'single':
        repos = [event['repository']]
    elif event['scan_mode'] == 'subset':
        repos = event['repositories']
    elif event['scan_mode'] == 'incremental':
        # Only repos with new commits
        all_repos = await gh.get_repos()
        repos = []
        for repo in all_repos:
            last_commit = memory.get_last_commit(repo)
            commits = await gh.get_repo_commits(repo, event['branch'])
            if not last_commit or (commits and commits[0]['sha'] != last_commit):
                repos.append(repo)
    else:
        raise ValueError('Unknown scan_mode')

    async def process_repo(repo):
        # Fetch latest commits
        commits = await gh.get_repo_commits(repo, event['branch'])
        last_commit = memory.get_last_commit(repo)
        if not commits:
            return None
        latest_commit = commits[0]['sha']
        if last_commit == latest_commit and not event['force_rescan']:
            return None
        # Extract diff
        if last_commit:
            diff_data = await gh.get_commit_diff(repo, latest_commit)
            files_changed = diff_data.get('files', [])
            code_changes = []
            for f in files_changed:
                if f['filename'].endswith('.py'):
                    code_changes.extend(extract_python_changes(f.get('patch', '')))
        else:
            code_changes = ['Initial scan: all code']
        # Documentation state (simplified: just README.md)
        readme_path = os.path.join('/tmp', f'{repo}_README.md')
        # Download README (simulate)
        # ...
        docs_state = 'README content here.'
        # Reason about impact
        reasoning = await agent.reason_about_impact(code_changes, docs_state)
        # Plan doc update (simulate)
        update_plan = {'API': 'Add new endpoint docs'} if code_changes else {}
        # Apply doc edits (simulate)
        # doc_editor.update_readme(readme_path, update_plan)
        # Validate docs (simulate)
        # doc_editor.validate_openapi(...)
        # Create PR (simulate branch)
        pr = await create_drift_pr(
            config, repo, 'drift-fix', event['branch'], code_changes, update_plan, reasoning, 'Checks passed', '0.95')
        # Update memory
        memory.set_last_commit(repo, latest_commit)
        memory.add_execution_history(repo, {
            'commit': latest_commit,
            'code_changes': code_changes,
            'reasoning': reasoning,
            'update_plan': update_plan
        })
        return pr

    # Run all repos in parallel
    results = await asyncio.gather(*(process_repo(repo) for repo in repos))
    return results
