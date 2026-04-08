# Visual Scripting Snippets

Unity Visual Scripting uses graph-based assets (.asset files) that cannot be represented as text code snippets. This folder provides guidance on common graph patterns instead.

## Recommended Graph Patterns

### Movement Controller (Script Graph)
- On Update event -> Get Input System Move value -> Multiply by speed -> Set Rigidbody velocity
- Use Object variables for component references (Rigidbody, Transform)

### Health System (Script Graph)
- Custom Event "OnDamaged" with int parameter
- Subtract from health variable -> Clamp between 0 and max -> Update UI
- Branch: if health <= 0 -> trigger "OnDied" custom event

### AI State Machine (State Graph)
- States: Idle, Patrol, Chase, Attack, Dead
- Transitions based on distance to player, health, line of sight
- Each state is a Script Graph defining behavior

### UI Button Handler (Script Graph)
- On Button Click event -> Play audio -> Load scene or toggle panel

### Timer System (Script Graph)
- On Update -> Subtract deltaTime from timer variable
- Branch: if timer <= 0 -> Trigger custom event -> Reset timer

## Tips

- Use Subgraphs (formerly SuperUnits) to extract reusable logic
- Use Sticky Notes to document complex flows
- Keep each graph under 20-30 nodes; split large graphs into Subgraphs
- Use Object variables instead of Find calls for component references
- Create custom C# Units for math-heavy or performance-critical operations
