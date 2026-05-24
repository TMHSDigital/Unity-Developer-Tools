---
title: Multiplayer Networking
description: Multiplayer networking patterns with Netcode for GameObjects, Netcode for Entities, Mirror, and Photon Fusion.
globs: ["**/*.cs"]
standards-version: 1.10.0
---

# Multiplayer Networking

## Choosing a Solution

Pick based on your game's scale and genre:

| Solution | Best For | Player Count | Complexity |
|----------|----------|--------------|------------|
| Netcode for GameObjects (NGO) | Casual co-op, small groups | 2-16 | Low-Medium |
| Netcode for Entities (NFE) | Competitive action, large scale | 64+ | High |
| Photon Fusion 2 | Fast-paced PvP, high frequency | 100+ | Medium |
| Mirror | Open-source indie, full control | 32-64 | Medium |

## Netcode for GameObjects (NGO)

Unity's official networking for MonoBehaviour workflows.

### Setup

1. Add NetworkManager to the scene
2. Add NetworkObject to any networked GameObject
3. Add NetworkBehaviour scripts for networked logic

### NetworkVariables

Synchronized state across all clients:

```csharp
public class PlayerHealth : NetworkBehaviour
{
    private NetworkVariable<int> _health = new(
        100,
        NetworkVariableReadPermission.Everyone,
        NetworkVariableWritePermission.Server
    );

    public override void OnNetworkSpawn()
    {
        _health.OnValueChanged += OnHealthChanged;
    }

    private void OnHealthChanged(int oldValue, int newValue)
    {
        UpdateHealthUI(newValue);
    }
}
```

### RPCs

Remote procedure calls for event-driven communication:

```csharp
// Client requests the server to do something
[ServerRpc]
private void TakeDamageServerRpc(int amount)
{
    if (!IsServer) return;
    _health.Value -= amount;

    if (_health.Value <= 0)
    {
        DieClientRpc();
    }
}

// Server tells all clients something happened
[ClientRpc]
private void DieClientRpc()
{
    PlayDeathAnimation();
}
```

### Ownership

- By default, the server owns all objects
- Transfer ownership for player-controlled objects: `NetworkObject.ChangeOwnership(clientId)`
- Check ownership: `IsOwner`, `IsServer`, `IsClient`, `IsLocalPlayer`

### Distributed Authority (Unity 6.4)

New mode for client-hosted games with shared authority:
- No dedicated server required
- Clients share ownership of objects
- Reduces latency for certain game types
- Configure in NetworkManager settings

## Netcode for Entities (NFE)

Built on ECS/DOTS for massive-scale competitive games.

- Client-side prediction out of the box
- Interpolation and lag compensation
- Ghost system for entity synchronization
- Requires DOTS knowledge (IComponentData, SystemBase)

Best for: battle royales, MMO combat, large-scale simulations.

## Photon Fusion 2

Third-party, cloud-based networking with excellent performance:

- Tick-based simulation with rollback support
- Host mode and dedicated server mode
- Built-in matchmaking and lobby system
- Excellent documentation and community

```csharp
public class NetworkedPlayer : NetworkBehaviour
{
    [Networked] public float Health { get; set; }
    [Networked] public Vector3 Position { get; set; }

    public override void FixedUpdateNetwork()
    {
        if (GetInput(out NetworkInputData input))
        {
            Position += input.Direction * Runner.DeltaTime * _moveSpeed;
        }
    }
}
```

## Mirror

Open-source, community-maintained networking:

- Drop-in replacement for the old UNet API
- SyncVar for state synchronization
- Command/ClientRpc for communication
- Many community transports (WebSocket, Steam, KCP)

```csharp
public class PlayerCombat : NetworkBehaviour
{
    [SyncVar(hook = nameof(OnHealthChanged))]
    public int health = 100;

    [Command]
    public void CmdTakeDamage(int amount)
    {
        health -= amount;
    }

    private void OnHealthChanged(int oldValue, int newValue)
    {
        UpdateHealthBar(newValue);
    }
}
```

## General Networking Principles

- **Server Authority**: Server validates all game state changes. Clients send input, server processes it. Prevents cheating.
- **Client Authority**: Clients control their own state directly. Simpler but vulnerable to cheating. Only use for non-competitive games.
- **Lag Compensation**: Server rewinds game state to the time the client fired, checks hit detection, then applies the result.
- **Interpolation**: Smooth remote player movement between network updates.
- **Prediction**: Client predicts the result of its own input immediately. Server corrects if the prediction was wrong.
- **Always validate on the server**: Never trust client data in competitive games.
