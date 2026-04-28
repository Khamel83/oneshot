"""oneshot memory — repo-first memory operations."""

from __future__ import annotations

import click

from oneshot_cli import memory


@click.group("memory")
def cli():
    """Manage repo-first memory for OneShot and customer repos."""


@cli.command("scaffold")
@click.option(
    "--repo",
    type=click.Path(path_type=str),
    default=None,
    help="Target repo root (default: cwd)",
)
@click.option(
    "--mode",
    type=click.Choice(sorted(memory.POLICY_MODES)),
    default="isolated",
    show_default=True,
)
@click.option(
    "--force", is_flag=True, help="Overwrite scaffolded files if they already exist"
)
def scaffold_cmd(repo, mode, force):
    """Create the standard repo-local memory scaffold."""
    result = memory.scaffold(repo=repo, mode=mode, force=force)
    click.echo(f"Scaffolded memory for: {result['repo_root']}")
    if result["created"]:
        for path in result["created"]:
            click.echo(f"  created: {path}")
    else:
        click.echo("  no files created (scaffold already present)")


@cli.command("promote")
@click.argument(
    "kind", type=click.Choice(["decision", "blocker", "runbook", "session"])
)
@click.option(
    "--repo",
    type=click.Path(path_type=str),
    default=None,
    help="Target repo root (default: cwd)",
)
@click.option("--title", required=True, help="Short title")
@click.option("--summary", default="", help="Summary text (used by decision/session)")
@click.option("--rationale", default="", help="Rationale text for decisions")
@click.option("--blocker", "blocker_text", default="", help="Blocker text")
@click.option("--resolution", default="", help="Resolution text for blockers")
@click.option("--when-to-use", default="", help="When to use this runbook")
@click.option("--procedure", default="", help="Runbook command/procedure")
@click.option("--notes-text", default="", help="Human-facing notes for runbooks")
@click.option("--status", default="", help="Status override")
@click.option("--source-tool", default="manual", show_default=True)
@click.option("--source-session", default="local-session", show_default=True)
@click.option("--source-type", default="manual-promotion", show_default=True)
@click.option(
    "--confidence",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    show_default=True,
)
@click.option("--notes", default="", help="Provenance notes")
@click.option("--supersedes", default="", help="Prior decision reference")
def promote_cmd(
    kind,
    repo,
    title,
    summary,
    rationale,
    blocker_text,
    resolution,
    when_to_use,
    procedure,
    notes_text,
    status,
    source_tool,
    source_session,
    source_type,
    confidence,
    notes,
    supersedes,
):
    """Promote stable memory or capture a session summary with provenance."""
    if kind == "decision":
        if not summary or not rationale:
            raise click.ClickException("decision requires --summary and --rationale")
        result = memory.promote_decision(
            repo,
            title=title,
            summary=summary,
            rationale=rationale,
            status=status or "active",
            source_tool=source_tool,
            source_session=source_session,
            source_type=source_type,
            confidence=confidence,
            notes=notes,
            supersedes=supersedes,
        )
    elif kind == "blocker":
        if not blocker_text:
            raise click.ClickException("blocker requires --blocker")
        result = memory.promote_blocker(
            repo,
            title=title,
            blocker=blocker_text,
            resolution=resolution,
            status=status or ("resolved" if resolution else "active"),
            source_tool=source_tool,
            source_session=source_session,
            source_type=source_type,
            confidence=confidence,
            notes=notes,
        )
    elif kind == "runbook":
        if not when_to_use or not procedure:
            raise click.ClickException("runbook requires --when-to-use and --procedure")
        result = memory.promote_runbook(
            repo,
            title=title,
            when_to_use=when_to_use,
            procedure=procedure,
            notes_text=notes_text,
            source_tool=source_tool,
            source_session=source_session,
            source_type=source_type,
            confidence=confidence,
            notes=notes,
        )
    else:
        if not summary:
            raise click.ClickException("session requires --summary")
        result = memory.capture_session_summary(
            repo,
            title=title,
            summary=summary,
            source_tool=source_tool,
            source_session=source_session,
            confidence=confidence,
            notes=notes,
        )

    click.echo(f"Wrote: {result['target']}")
    click.echo(f"Provenance: {result['provenance']}")


@cli.command("retrieve")
@click.argument("query")
@click.option(
    "--repo",
    type=click.Path(path_type=str),
    default=None,
    help="Target repo root (default: cwd)",
)
@click.option("--limit", type=int, default=10, show_default=True)
@click.option(
    "--include-cross-repo",
    is_flag=True,
    help="Append abstracted cross-repo results from the private index",
)
def retrieve_cmd(query, repo, limit, include_cross_repo):
    """Retrieve same-repo memory in deterministic priority order."""
    results = memory.retrieve_same_repo(repo, query, limit=limit)
    if not results and not include_cross_repo:
        click.echo("No matching memory found.")
        return
    for idx, result in enumerate(results, start=1):
        click.echo(f"[{idx}] {result.title}")
        click.echo(f"  source: {result.source}")
        click.echo(f"  score: {result.score}  priority: {result.priority}")
        if result.conflicted:
            click.echo("  conflicted: yes")
        if result.superseded:
            click.echo("  superseded: yes")
        click.echo(f"  snippet: {result.body}")
    if include_cross_repo:
        cross_repo = memory.search_cross_repo_abstractions(
            query, current_repo=repo, limit=limit
        )
        if cross_repo["status"] != "ok":
            click.echo(
                f"degraded mode: cross-repo search unavailable ({cross_repo['reason']})"
            )
            return
        if cross_repo["results"]:
            click.echo("\nCross-repo abstractions:")
            for idx, result in enumerate(cross_repo["results"], start=1):
                click.echo(f"[{idx}] {result['title']}")
                click.echo(f"  repo: {result['repo_name']}")
                click.echo(f"  source: {result['source_path']}")
                click.echo(
                    f"  sensitivity: {result['sensitivity']}  score: {result['score']}"
                )
                click.echo(f"  snippet: {result['snippet']}")
        elif not results:
            click.echo("No matching memory found.")


@cli.command("abstract")
@click.option(
    "--repo",
    type=click.Path(path_type=str),
    default=None,
    help="Target repo root (default: cwd)",
)
@click.option("--title", required=True)
@click.option("--lesson", required=True)
@click.option(
    "--category",
    type=click.Choice(
        ["tooling", "infra", "orchestration", "debugging", "runbook", "governance"]
    ),
    required=True,
)
@click.option(
    "--trust",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    show_default=True,
)
@click.option(
    "--sensitivity",
    type=click.Choice(sorted(memory.POLICY_MODES)),
    default="portable",
    show_default=True,
)
@click.option("--removed-details", default="")
@click.option("--promotes-from", default="")
def abstract_cmd(
    repo, title, lesson, category, trust, sensitivity, removed_details, promotes_from
):
    """Create a cross-repo abstraction record for future private indexing."""
    result = memory.create_abstraction(
        repo,
        title=title,
        lesson=lesson,
        category=category,
        trust=trust,
        sensitivity=sensitivity,
        removed_details=removed_details,
        promotes_from=promotes_from,
    )
    click.echo(f"Wrote abstraction: {result['target']}")


@cli.command("index")
@click.option(
    "--repo",
    type=click.Path(path_type=str),
    default=None,
    help="Target repo root (default: cwd)",
)
def index_cmd(repo):
    """Index repo-local durable memory and abstractions into the private global store."""
    result = memory.index_repo_memory(repo)
    click.echo(f"Indexed repo: {result['repo_root']}")
    click.echo(f"  documents: {result['indexed']}")
    click.echo(f"  db: {result['db']}")


@cli.command("search")
@click.argument("query")
@click.option(
    "--repo",
    type=click.Path(path_type=str),
    default=None,
    help="Current repo root for excluding self results",
)
@click.option("--limit", type=int, default=10, show_default=True)
def search_cmd(query, repo, limit):
    """Search abstracted cross-repo memory in the private global store."""
    result = memory.search_cross_repo_abstractions(
        query, current_repo=repo, limit=limit
    )
    if result["status"] != "ok":
        click.echo(f"degraded mode: cross-repo search unavailable ({result['reason']})")
        return
    if not result["results"]:
        click.echo("No cross-repo abstractions found.")
        return
    for idx, item in enumerate(result["results"], start=1):
        click.echo(f"[{idx}] {item['title']}")
        click.echo(f"  repo: {item['repo_name']}")
        click.echo(f"  source: {item['source_path']}")
        click.echo(f"  sensitivity: {item['sensitivity']}  score: {item['score']}")
        click.echo(f"  snippet: {item['snippet']}")
