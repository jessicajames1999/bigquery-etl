#!/usr/bin/env python3
"""
Update schema.yaml from GitHub issue containing JSON descriptions.

This script is called by GitHub Actions to process approved issues
and update column descriptions in schema.yaml files.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from ruamel.yaml import YAML


def fetch_issue_body(repo, issue_number, token):
    """Fetch issue body from GitHub API."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()["body"]


def parse_issue_body(body):
    """Parse JSON from issue body."""
    try:
        data = json.loads(body.strip())
        
        # Validate structure
        if "table" not in data:
            raise ValueError("Missing 'table' field in JSON")
        if "descriptions" not in data:
            raise ValueError("Missing 'descriptions' field in JSON")
        
        return data["table"], data["descriptions"]
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in issue body: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def parse_table_name(table_full_name):
    """Parse database.dataset.table into components."""
    parts = table_full_name.split(".")
    if len(parts) != 3:
        print(f"Error: Invalid table name format: {table_full_name}")
        print("Expected format: database.dataset.table")
        sys.exit(1)
    
    return parts[0], parts[1], parts[2]


def find_schema_file(database, dataset, table):
    """Find the schema.yaml file path."""
    schema_path = Path(f"sql/{database}/{dataset}/{table}/schema.yaml")
    
    if not schema_path.exists():
        print(f"Error: Schema file not found at: {schema_path}")
        sys.exit(1)
    
    return schema_path


def load_schema(schema_path):
    """Load and parse schema.yaml file."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    
    with open(schema_path, 'r') as f:
        data = yaml.load(f)
    
    return data, yaml


def update_descriptions(schema_data, descriptions):
    """Update descriptions in schema data."""
    updated_count = 0
    
    for field in schema_data['fields']:
        column_name = field['name']
        if column_name in descriptions:
            field['description'] = descriptions[column_name]
            updated_count += 1
    
    return updated_count


def save_schema(schema_path, schema_data, yaml):
    """Save updated schema back to file."""
    with open(schema_path, 'w') as f:
        yaml.dump(schema_data, f)


def set_github_output(name, value):
    """Set GitHub Actions output variable."""
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"{name}={value}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Update schema.yaml from GitHub issue"
    )
    parser.add_argument("--issue-number", required=True, type=int,
                       help="GitHub issue number")
    parser.add_argument("--repo", required=True,
                       help="Repository in format owner/repo")
    parser.add_argument("--token", required=True,
                       help="GitHub token")
    
    args = parser.parse_args()
    
    print(f"Processing issue #{args.issue_number}...")
    
    # Fetch issue body
    issue_body = fetch_issue_body(args.repo, args.issue_number, args.token)
    print("✓ Fetched issue body")
    
    # Parse JSON
    table_name, descriptions = parse_issue_body(issue_body)
    print(f"✓ Parsed table: {table_name}")
    print(f"✓ Found {len(descriptions)} column descriptions")
    
    # Parse table name
    database, dataset, table = parse_table_name(table_name)
    
    # Find schema file
    schema_path = find_schema_file(database, dataset, table)
    print(f"✓ Found schema at: {schema_path}")
    
    # Load schema
    schema_data, yaml = load_schema(schema_path)
    total_columns = len(schema_data['fields'])
    print(f"✓ Loaded schema with {total_columns} columns")
    
    # Update descriptions
    updated_count = update_descriptions(schema_data, descriptions)
    print(f"✓ Updated {updated_count} column descriptions")
    
    # Save schema
    save_schema(schema_path, schema_data, yaml)
    print(f"✓ Saved updated schema to {schema_path}")
    
    # Set GitHub Actions outputs
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    branch_suffix = f"{database}-{dataset}-{table}-{timestamp}"
    
    set_github_output("table_name", table_name)
    set_github_output("branch_suffix", branch_suffix)
    set_github_output("columns_updated", str(updated_count))
    
    print(f"\n✅ Successfully updated {updated_count}/{total_columns} columns!")


if __name__ == "__main__":
    main()