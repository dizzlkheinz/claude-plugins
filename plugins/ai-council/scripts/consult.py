#!/usr/bin/env python3
"""
AI Council Consultation Script

Orchestrates multi-AI discussions between Claude, Gemini, Codex CLIs and Perplexity API.
"""

import subprocess
import sys
import json
import argparse
import os
import urllib.request
import urllib.error
from typing import Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class AIAgent:
    name: str
    command: list[str] = field(default_factory=list)
    available: bool = True
    is_api: bool = False  # True if uses API instead of CLI


def check_cli_available(command: str) -> bool:
    """Check if a CLI tool is available."""
    try:
        subprocess.run(
            ["where" if sys.platform == "win32" else "which", command],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_perplexity_available() -> bool:
    """Check if Perplexity API key is set."""
    return bool(os.environ.get("PERPLEXITY_API_KEY"))


def query_perplexity_api(prompt: str, timeout: int = 120) -> tuple[str, str, Optional[str]]:
    """Query Perplexity via API."""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        return ("Perplexity", "", "PERPLEXITY_API_KEY not set")

    url = "https://api.perplexity.ai/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "preset": "sonar",
        "input": prompt
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            output = result.get("output", str(result))
            return ("Perplexity", output, None)
    except urllib.error.HTTPError as e:
        return ("Perplexity", "", f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        return ("Perplexity", "", f"URL Error: {e.reason}")
    except TimeoutError:
        return ("Perplexity", "", f"Timeout after {timeout}s")
    except Exception as e:
        return ("Perplexity", "", str(e))


def get_agents() -> dict[str, AIAgent]:
    """Get available AI agents."""
    agents = {
        "claude": AIAgent(
            name="Claude",
            command=["claude", "-p"],
            available=check_cli_available("claude")
        ),
        "gemini": AIAgent(
            name="Gemini",
            command=["gemini", "-p"],
            available=check_cli_available("gemini")
        ),
        "codex": AIAgent(
            name="Codex",
            command=["codex", "exec"],
            available=check_cli_available("codex")
        ),
        "perplexity": AIAgent(
            name="Perplexity",
            command=[],
            available=check_perplexity_available(),
            is_api=True
        ),
    }
    return agents


def query_agent(agent: AIAgent, prompt: str, timeout: int = 120) -> tuple[str, str, Optional[str]]:
    """
    Query an AI agent and return its response.

    Returns: (agent_name, response, error)
    """
    if not agent.available:
        if agent.is_api:
            return (agent.name, "", f"{agent.name} API key not configured")
        return (agent.name, "", f"{agent.name} CLI not available")

    # Special handling for API-based agents
    if agent.is_api:
        if agent.name == "Perplexity":
            return query_perplexity_api(prompt, timeout)
        return (agent.name, "", f"Unknown API agent: {agent.name}")

    try:
        cmd = agent.command + [prompt]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )

        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr:
            output += f"\n[stderr: {result.stderr.strip()}]"

        return (agent.name, output, None)

    except subprocess.TimeoutExpired:
        return (agent.name, "", f"Timeout after {timeout}s")
    except Exception as e:
        return (agent.name, "", str(e))


def format_previous_responses(responses: dict[str, str]) -> str:
    """Format previous responses for inclusion in prompts."""
    parts = []
    for agent_name, response in responses.items():
        if response:
            parts.append(f"--- {agent_name} ---\n{response}\n")
    return "\n".join(parts)


def run_consultation(
    question: str,
    agents: dict[str, AIAgent],
    selected_agents: Optional[list[str]] = None,
    rounds: int = 2,
    timeout: int = 120,
    output_format: str = "text"
) -> dict:
    """
    Run a multi-round consultation.

    Args:
        question: The question to discuss
        agents: Available AI agents
        selected_agents: Which agents to include (None = all available)
        rounds: Number of discussion rounds
        timeout: Timeout per query in seconds
        output_format: "text" or "json"

    Returns:
        Consultation results
    """
    # Filter to selected agents
    if selected_agents:
        agents = {k: v for k, v in agents.items() if k in selected_agents}

    # Filter to available agents
    available_agents = {k: v for k, v in agents.items() if v.available}

    if not available_agents:
        return {"error": "No AI agents available"}

    results = {
        "question": question,
        "rounds": [],
        "participants": list(available_agents.keys()),
        "unavailable": [k for k, v in agents.items() if not v.available]
    }

    all_responses: dict[str, str] = {}

    for round_num in range(1, rounds + 1):
        round_results = {"round": round_num, "responses": {}, "errors": {}}

        # Build prompt for this round
        if round_num == 1:
            prompt_template = (
                "You are participating in a multi-AI consultation. "
                "Answer the following question thoughtfully and concisely (2-3 paragraphs).\n\n"
                f"Question: {question}"
            )
        else:
            prev_formatted = format_previous_responses(all_responses)
            prompt_template = (
                "You are participating in a multi-AI consultation. "
                "Here is the question and responses from the previous round:\n\n"
                f"Question: {question}\n\n"
                f"Previous responses:\n{prev_formatted}\n\n"
                "Consider these perspectives. Do you agree, disagree, or have additional insights? "
                "Be concise (2-3 paragraphs)."
            )

        # Query all agents in parallel
        with ThreadPoolExecutor(max_workers=len(available_agents)) as executor:
            futures = {
                executor.submit(query_agent, agent, prompt_template, timeout): name
                for name, agent in available_agents.items()
            }

            for future in as_completed(futures):
                agent_name, response, error = future.result()
                if error:
                    round_results["errors"][agent_name] = error
                else:
                    round_results["responses"][agent_name] = response
                    all_responses[agent_name] = response

        results["rounds"].append(round_results)

        # Print progress in text mode
        if output_format == "text":
            print(f"\n{'='*60}")
            print(f"ROUND {round_num}")
            print('='*60)
            for name, response in round_results["responses"].items():
                print(f"\n--- {name} ---")
                print(response)
            for name, error in round_results["errors"].items():
                print(f"\n--- {name} (ERROR) ---")
                print(error)

    return results


def main():
    parser = argparse.ArgumentParser(description="AI Council Consultation")
    parser.add_argument("question", nargs="?", help="Question to discuss")
    parser.add_argument("--agents", "-a", nargs="+", choices=["claude", "gemini", "codex", "perplexity"],
                        help="Which agents to include (default: all)")
    parser.add_argument("--rounds", "-r", type=int, default=2,
                        help="Number of discussion rounds (default: 2)")
    parser.add_argument("--timeout", "-t", type=int, default=120,
                        help="Timeout per query in seconds (default: 120)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--list-agents", "-l", action="store_true",
                        help="List available agents and exit")

    args = parser.parse_args()

    agents = get_agents()

    if args.list_agents:
        print("Available AI Agents:")
        for key, agent in agents.items():
            if agent.is_api:
                status = "API configured" if agent.available else "API key not set"
            else:
                status = "CLI available" if agent.available else "CLI not found"
            print(f"  {key}: {agent.name} [{status}]")
        return

    if not args.question:
        parser.error("question is required")

    results = run_consultation(
        question=args.question,
        agents=agents,
        selected_agents=args.agents,
        rounds=args.rounds,
        timeout=args.timeout,
        output_format=args.format
    )

    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif args.format == "text":
        print("\n" + "="*60)
        print("CONSULTATION COMPLETE")
        print("="*60)
        if results.get("unavailable"):
            print(f"Unavailable agents: {', '.join(results['unavailable'])}")


if __name__ == "__main__":
    main()
