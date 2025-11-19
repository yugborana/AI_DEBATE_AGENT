from typing import Dict


def format_markdown_summary(state: Dict) -> str:
    lines = [f"# Debate: {state['topic']}"]
    lines.append("\n## Stances")
    lines.append(f"- **A:** {state['stance_a']}")
    lines.append(f"- **B:** {state['stance_b']}")


    lines.append("\n## Opening Arguments")
    lines.append(f"**A:**\n{state['argument_a']}")
    lines.append(f"\n**B:**\n{state['argument_b']}")


    if state.get("rebuttals_a"):
        lines.append("\n## Rebuttals (A → B)")
        lines.append(state["rebuttals_a"])
    if state.get("rebuttals_b"):
        lines.append("\n## Rebuttals (B → A)")
        lines.append(state["rebuttals_b"])


    if state.get("verdict"):
        lines.append("\n## Verdict")
        lines.append(state["verdict"])
    return "\n".join(lines)