# CTO Feedback on ONE_SHOT v11 Roadmap

**Date**: 2026-02-06
**Reviewer**: Gemini CLI (as CTO)
**Status**: Phase 1 Approved with conditions.

This review is based on the `CTO-review-package.md`. The analysis is clear and the findings are actionable. This is excellent work.

My feedback is organized by the requested categories.

---

### 1. Strategic Feedback

The proposed direction is **100% correct**. Our decision to simplify in v10 was a strategic bet that the platform would mature, and `claude-sneakpeek` validates this bet.

- **"Wait for Native" is the right vision.** Our core value is developer productivity, not building foundational orchestration. By aligning with the native stack, we reduce our maintenance burden and focus on the unique value ONE_SHOT provides: a seamless, terminal-first developer experience. We should be the best *client* for these emerging agentic features, not a competing framework.

- **The task management strategy is sound.** The `native` first, `beads` fallback approach is pragmatic. `beads` is our insurance policy against platform delays. It's simple, git-backed, and it works. Let's treat it as a stable bridge, not a liability to be rushed out.

- **The OpenClaw scope boundary is correct.** We are a developer productivity tool. Expanding into general-purpose AI assistance with multiple channels (voice, messaging) would be a critical strategic error, pulling focus from our core user base.

### 2. Priority Adjustments

The phasing is mostly correct, with one key adjustment.

1.  **Phase 1: Documentation (Approved)**: **Proceed immediately.** Clear communication is critical. We must set expectations with users now regarding the "wait for native" strategy and the future of `beads`. Add the deprecation notice to `beads` docs, but frame it as a long-term transition, not an imminent removal.

2.  **Phase 2: Progressive Disclosure (On Hold)**: **Do not proceed yet.** The token savings needs to be quantified. Is the implementation complexity worth the benefit? Provide a brief analysis showing token usage before and after for a typical large project. If the savings are not an order of magnitude, we defer this. Simplicity trumps micro-optimization.

3.  **Phase 3: Task Tools Transition (Correct Priority)**: This is rightly dependent on the native tool release. The plan to auto-switch is good, but needs to be handled with care to avoid a jarring user experience.

4.  **Phase 4: Clean Up (Correct Priority)**: This logically follows a successful transition.

### 3. Risk Concerns

The package identified the key risks. Here is my perspective on them and one additional concern.

-   **Risk: Native Tools Delayed.** This is the most significant risk.
    -   **Mitigation**: We fully embrace `beads` as our stable, long-term bridge. We do not treat it as a temporary hack. It works, it's reliable, and it aligns with our git-based ethos. If the delay is indefinite, we can reconsider investing more in `beads`, but for now, it's a perfect fallback.

-   **Risk: Beads Abandonment.**
    -   **Mitigation**: Do not deprecate `beads` too early. The deprecation warning should state that `beads` will be phased out *after* native tools are stable and widely available. We will support `beads` for at least one major version after the native transition is complete to ensure a smooth runway for users.

-   **Risk: Scope Creep.**
    -   **Mitigation**: The analysis of OpenClaw proves the team is vigilant about this. We will continue to use "Does this directly improve terminal-based developer productivity?" as our guiding question for all new features.

-   **NEW Risk: User Experience During Transition.**
    -   **Concern**: An "auto-switch" from `beads` to native tools could be confusing. A user's workflow might suddenly change.
    -   **Mitigation**: The migration must be explicit. When native tools are first detected, ONE_SHOT should inform the user, explain the benefits, and ask if they want to migrate their tasks or switch the default. We should provide a one-time command `beads migrate-to-native` rather than doing it silently.

### 4. Approval Decision

**Phase 1 is approved.** Proceed with updating the documentation as outlined.

**Phase 2 is on hold** pending a cost-benefit analysis of the token savings.

We will revisit the full roadmap once Phase 1 is complete and the native tooling landscape becomes clearer. This is the pragmatic path forward.
