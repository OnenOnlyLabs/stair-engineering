# Room 204 — How this system is wired

<!-- toc -->
Sections (4) — read only what you need:
- Layers — Layer 1 (stairs/layer1/MEMORY.md) is loaded on every call. L…
- Loading — tools/stairload.py prints exactly what to inject. Layer 1 al…
- Keeping it honest — tools/stairtoc.py check finds rooms nothing points to, route…
- Changes
<!-- /toc -->

## Layers
Layer 1 (`stairs/layer1/MEMORY.md`) is loaded on every call. Layer 2 (`stairs/layer2/`) is opened by room address only when needed. Layer 3 (`stairs/layer3/`) is one identity card per agent.

## Loading
`tools/stair_load.py` prints exactly what to inject. Layer 1 always; a Layer 3 card with `--agent`; a room's TOC with `--room`; one section with `--section`; keyword routing with `--route`.

## Keeping it honest
`tools/stair_toc.py check` finds rooms nothing points to, routes that point at nothing, and prints the Layer 1 size so you notice when it grows.

## Changes
- (add one line here every time you change the wiring — who, what, why)
