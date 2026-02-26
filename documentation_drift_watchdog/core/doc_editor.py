import os
import re
import yaml
from ruamel.yaml import YAML
from markdown_it import MarkdownIt

class DocumentationEditor:
    def __init__(self):
        self.md = MarkdownIt()
        self.yaml = YAML()

    def update_readme(self, readme_path, update_plan):
        with open(readme_path, 'r') as f:
            content = f.read()
        # Apply minimal updates based on plan (string replace or section insert)
        for section, new_text in update_plan.items():
            pattern = rf'(#+\s*{re.escape(section)}.*?)(\n#+|\Z)'
            content = re.sub(pattern, f"\\1\n{new_text}\2", content, flags=re.DOTALL)
        with open(readme_path, 'w') as f:
            f.write(content)

    def update_openapi(self, openapi_path, update_plan):
        with open(openapi_path, 'r') as f:
            data = self.yaml.load(f)
        # Apply updates to OpenAPI spec
        for path, method_spec in update_plan.items():
            data['paths'][path] = method_spec
        with open(openapi_path, 'w') as f:
            self.yaml.dump(data, f)

    def validate_openapi(self, openapi_path):
        from openapi_spec_validator import validate_spec
        with open(openapi_path, 'r') as f:
            data = self.yaml.load(f)
        validate_spec(data)
