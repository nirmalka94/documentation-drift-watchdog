
import openai
import os
import yaml
import httpx

class ReasoningAgent:
    def __init__(self, config):
        self.config = config
        self.llm_provider = config.get('LLM_PROVIDER', 'openai')
        self.model = config.get('OPENAI_MODEL', 'gpt-4')
        self.ollama_model = config.get('OLLAMA_MODEL', 'llama2')
        api_key = config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        openai.api_key = api_key


    async def reason_about_impact(self, code_changes, docs_state):
        prompt = self.build_prompt(code_changes, docs_state)
        if self.llm_provider == 'openai':
            response = await self.openai_chat(prompt)
            return response
        elif self.llm_provider == 'ollama':
            response = await self.ollama_chat(prompt)
            return response
        return None

    def build_prompt(self, code_changes, docs_state):
        return f"""
You are a Documentation Drift Watchdog Agent.

Code changes:
{code_changes}

Current documentation state:
{docs_state}

Analyze the impact of the code changes on documentation. List only affected documentation sections and propose minimal, precise updates. Explain your reasoning. Do not invent APIs. Do not rewrite unrelated docs.
"""

    async def openai_chat(self, prompt):
        client = openai.AsyncOpenAI(api_key=openai.api_key)
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a documentation drift detection agent."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def ollama_chat(self, prompt):
        # Assumes Ollama is running locally on default port
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": "You are a documentation drift detection agent."},
                {"role": "user", "content": prompt}
            ]
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            # Ollama returns the response in 'message' or 'response' key
            if 'message' in data and 'content' in data['message']:
                return data['message']['content']
            elif 'response' in data:
                return data['response']
            return str(data)
