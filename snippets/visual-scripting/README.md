# Visual Scripting Patterns

Script Graphs and State Graphs are saved as Unity YAML assets (`.asset`) whose node data is serialized JSON. They are text, but not readable or hand-editable in any useful way, so this folder describes common graph patterns instead of shipping graph files. Build them in the graph editor from these outlines.

## Recommended Graph Patterns

### Movement Controller (Script Graph)
- On Update event -> Get Input System Move value -> Multiply by speed -> Set Rigidbody `linearVelocity` (Unity 6 renamed `velocity` to `linearVelocity`)
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
- Name graph assets with "Script Graph" or "State Graph" in the file name (Unity's default), or keep them under a `VisualScripting/` folder, so the plugin's visual scripting rule and skill attach to them
