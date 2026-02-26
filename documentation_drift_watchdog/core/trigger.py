import asyncio
from workflow.langgraph_workflow import run_workflow

def build_event_from_payload(payload):
    # Validate and normalize trigger event
    event = {
        'scan_mode': payload.get('scan_mode', 'all'),
        'repository': payload.get('repository', ''),
        'repositories': payload.get('repositories', []),
        'branch': payload.get('branch', 'main'),
        'force_rescan': payload.get('force_rescan', False)
    }
    return event

async def handle_trigger_event(payload, config):
    event = build_event_from_payload(payload)
    await run_workflow(event, config)
