"""oneshot lanes — print lane routing table."""
from __future__ import annotations

import click

from oneshot_cli.config import load_config


@click.command("lanes")
def cli():
    """Print the lane routing table."""
    cfg = load_config()
    lanes = cfg.get("lanes", {})
    providers = cfg.get("providers", {})

    # Header
    click.echo(f"{'LANE':<20} {'CURRENT PROVIDER+MODEL':<30} {'FUTURE PROVIDER+MODEL':<30} {'MAX_DIFF':<10} {'MAX_FILES':<10} {'ARCH'}")
    click.echo("-" * 110)

    for lane_name, lane in lanes.items():
        cp = lane.get("current_provider", "")
        cm = lane.get("current_model", "")
        fp = lane.get("future_provider", "")
        fm = lane.get("future_model", "")

        # Resolve display names
        current_display = _resolve_display(providers, cp, cm)
        future_display = _resolve_display(providers, fp, fm)

        # Check if future provider is enabled
        future_enabled = providers.get(fp, {}).get("enabled", False)
        if not future_enabled and fp:
            future_display += " (disabled)"

        max_diff = lane.get("max_diff_lines") or "unlimited"
        max_files = lane.get("max_files") or "unlimited"
        arch = "Y" if lane.get("allow_architecture_changes") else "N"

        click.echo(f"{lane_name:<20} {current_display:<30} {future_display:<30} {max_diff:<10} {max_files:<10} {arch}")


def _resolve_display(providers: dict, provider_key: str, model_key: str) -> str:
    if not provider_key or not model_key:
        return "-"
    provider = providers.get(provider_key, {})
    if provider_key == "claude_review":
        return "claude_review/manual"
    model = provider.get("models", {}).get(model_key, {})
    model_id = model.get("id", model_key)
    return f"{provider_key}/{model_id}"
