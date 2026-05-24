---
title: Visual Scripting
description: Unity Visual Scripting guidance for Script Graphs, State Graphs, Subgraphs, and custom units.
globs: ["**/*.asset"]
standards-version: 1.10.0
---

# Visual Scripting

## Overview

Unity Visual Scripting (com.unity.visualscripting) is a built-in, node-based programming system. It is designed for:

- Designers and non-programmers building game logic
- State machines for AI, dialog systems, and game flow
- Rapid prototyping of gameplay mechanics
- Exposing logic that needs frequent tweaking without recompilation

## Script Graphs vs State Graphs

### Script Graphs

Sequential flow of logic, similar to writing a function. Use for:
- Gameplay logic (on trigger enter, spawn effect, play sound)
- Event responses (button clicked, timer expired)
- Calculations and data processing

### State Graphs

Finite state machines with transitions. Use for:
- AI behavior (idle, patrol, chase, attack)
- Game states (menu, playing, paused, game over)
- Dialog systems (greeting, question, farewell)
- Animation-like sequences with conditions

## Graph Components

### Script Machine (formerly Flow Machine)

Attach a Script Machine component to a GameObject to run a Script Graph.

### State Machine

Attach a State Machine component to run a State Graph.

## Variables

Five scopes for storing data:

| Scope | Lifetime | Sharing |
|-------|----------|---------|
| Graph | While the graph runs | This graph only |
| Object | While the GameObject exists | All graphs on this GameObject |
| Scene | While the scene is loaded | All graphs in the scene |
| Application | While the application runs | All graphs everywhere |
| Saved | Persists between sessions | All graphs (uses PlayerPrefs) |

## Subgraphs (formerly SuperUnits)

Extract reusable logic into Subgraphs:

1. Select a group of nodes
2. Right-click > Convert to Subgraph
3. Define input and output ports
4. Reuse across multiple graphs

Keep Subgraphs small and focused. Name them descriptively. Use them to avoid duplicating logic.

## Custom Events

Communicate between graphs without direct references:

Trigger from a Script Graph:
- Use the "Custom Event" trigger node
- Set the event name (string) and arguments

Listen in another Script Graph:
- Use the "Custom Event" listener node
- Match the event name

Trigger from C#:

```csharp
using Unity.VisualScripting;

CustomEvent.Trigger(targetGameObject, "OnDamaged", damageAmount);
```

## Custom Units (C# Nodes)

Create custom nodes for performance-critical operations or complex logic:

```csharp
using Unity.VisualScripting;

[UnitTitle("Lerp Color")]
[UnitCategory("Custom/Color")]
public class LerpColorUnit : Unit
{
    [DoNotSerialize] public ValueInput colorA;
    [DoNotSerialize] public ValueInput colorB;
    [DoNotSerialize] public ValueInput t;
    [DoNotSerialize] public ValueOutput result;

    protected override void Definition()
    {
        colorA = ValueInput<Color>(nameof(colorA), Color.white);
        colorB = ValueInput<Color>(nameof(colorB), Color.black);
        t = ValueInput<float>(nameof(t), 0.5f);
        result = ValueOutput<Color>(nameof(result), flow =>
        {
            return Color.Lerp(flow.GetValue<Color>(colorA), flow.GetValue<Color>(colorB), flow.GetValue<float>(t));
        });
    }
}
```

After creating custom units, regenerate the node library: Edit > Project Settings > Visual Scripting > Regenerate Nodes.

## Best Practices

- Keep graphs small and focused. If a graph has more than 20-30 nodes, split it into Subgraphs.
- Use descriptive names for all variables and custom events.
- Add Sticky Notes to explain complex logic.
- Use Object variables for component references instead of repeated Find calls.
- Document graph inputs and outputs in the graph description field.
- Use State Graphs for anything with distinct behavioral modes.
- Move performance-critical or mathematically complex logic to C# custom units.

## When to Switch to C#

- The graph becomes too complex to read (visual spaghetti)
- Performance profiling shows the graph as a bottleneck
- The team is scaling and needs code review workflows
- The logic involves complex algorithms, data structures, or async operations
