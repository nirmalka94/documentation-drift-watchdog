import argparse
import yaml
import os
import sys
import asyncio
from core.trigger import handle_trigger_event

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def parse_args():
    parser = argparse.ArgumentParser(description='Documentation Drift Watchdog Agent')
    parser.add_argument('--mode', type=str, default=None, help='Execution mode: all, single, subset, incremental')
    parser.add_argument('--repo', type=str, default=None, help='Repository name for single mode')
    parser.add_argument('--repos', nargs='*', default=None, help='List of repositories for subset mode')
    parser.add_argument('--branch', type=str, default=None, help='Branch to scan')
    parser.add_argument('--force_rescan', action='store_true', help='Force rescan of all commits')
    parser.add_argument('--webapi', action='store_true', help='Run as web API server')
    return parser.parse_args()

async def main():
    args = parse_args()
    config = load_config()

    # CLI trigger
    if not args.webapi:
        trigger_payload = {
            'scan_mode': args.mode or config.get('EXECUTION_MODE', 'all'),
            'repository': args.repo or config.get('REPOSITORY', ''),
            'repositories': args.repos or config.get('REPOSITORIES', []),
            'branch': args.branch or config.get('DEFAULT_BRANCH', 'main'),
            'force_rescan': args.force_rescan or config.get('FORCE_RESCAN', False)
        }
        await handle_trigger_event(trigger_payload, config)
    else:
        from webapi.server import run_webapi
        await run_webapi(config)

if __name__ == '__main__':
    asyncio.run(main())
