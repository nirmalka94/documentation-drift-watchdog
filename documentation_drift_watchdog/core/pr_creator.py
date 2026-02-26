from github_tools.github_api import GitHubAPI

PR_TEMPLATE = """
## Documentation Drift Report

### Code Changes
{code_changes}

### Documentation Updated
{docs_updated}

### Reasoning
{reasoning}

### Safety Checks
{checks}

### Drift Confidence Score
{confidence}
"""

async def create_drift_pr(config, repo, branch, base, code_changes, docs_updated, reasoning, checks, confidence):
    gh = GitHubAPI(config['GITHUB_TOKEN'], config['GITHUB_USER_OR_ORG'])
    body = PR_TEMPLATE.format(
        code_changes=code_changes,
        docs_updated=docs_updated,
        reasoning=reasoning,
        checks=checks,
        confidence=confidence
    )
    title = "[Drift Watchdog] Documentation Drift Fix"
    return await gh.create_pull_request(repo, branch, base, title, body)
