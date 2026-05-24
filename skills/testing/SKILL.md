---
title: Unity Testing
description: Unity Test Framework usage for Edit Mode and Play Mode tests with async Awaitable support.
globs: ["**/Tests/**/*.cs", "**/*Tests*.cs", "**/*Test*.cs"]
standards-version: 1.10.0
---

# Unity Testing

## Unity Test Framework (UTF) 2.x

Unity uses NUnit as its testing foundation, extended with Unity-specific attributes and runners.

## Test Types

### Edit Mode Tests

Run without entering play mode. Test pure C# logic, ScriptableObject behavior, and editor tools.

```csharp
using NUnit.Framework;

public class HealthTests
{
    [Test]
    public void TakeDamage_ReducesHealth()
    {
        var health = new HealthComponent { Current = 100, Max = 100 };
        health.TakeDamage(25);
        Assert.AreEqual(75, health.Current);
    }

    [Test]
    public void TakeDamage_DoesNotGoBelowZero()
    {
        var health = new HealthComponent { Current = 10, Max = 100 };
        health.TakeDamage(50);
        Assert.AreEqual(0, health.Current);
    }

    [Test]
    public void Heal_DoesNotExceedMax()
    {
        var health = new HealthComponent { Current = 80, Max = 100 };
        health.Heal(50);
        Assert.AreEqual(100, health.Current);
    }
}
```

### Play Mode Tests

Run inside play mode with scene loading, physics, and full MonoBehaviour lifecycle.

```csharp
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

public class PlayerMovementTests
{
    [UnityTest]
    public IEnumerator Player_MovesForward_WhenInputApplied()
    {
        var playerGO = new GameObject("Player");
        var controller = playerGO.AddComponent<PlayerController>();

        Vector3 startPos = playerGO.transform.position;
        controller.SimulateInput(Vector2.up);

        yield return new WaitForSeconds(0.5f);

        Assert.Greater(playerGO.transform.position.z, startPos.z);

        Object.Destroy(playerGO);
    }
}
```

### Async Tests with Awaitable

Use async tests for modern Unity code:

```csharp
[Test]
public async System.Threading.Tasks.Task AsyncOperation_CompletesSuccessfully()
{
    var loader = new AssetLoader();
    var result = await loader.LoadConfigAsync();
    Assert.IsNotNull(result);
    Assert.AreEqual("default", result.Name);
}
```

## Assertions

```csharp
Assert.AreEqual(expected, actual);
Assert.AreNotEqual(unexpected, actual);
Assert.IsTrue(condition);
Assert.IsFalse(condition);
Assert.IsNull(obj);
Assert.IsNotNull(obj);
Assert.Greater(a, b);
Assert.Less(a, b);
Assert.That(value, Is.InRange(min, max));
Assert.Throws<ArgumentException>(() => DoSomething());

// Float comparison with tolerance
Assert.AreEqual(1.0f, actual, 0.001f);
```

## Test Fixtures

```csharp
public class InventoryTests
{
    private Inventory _inventory;

    [SetUp]
    public void SetUp()
    {
        _inventory = new Inventory(maxSlots: 10);
    }

    [TearDown]
    public void TearDown()
    {
        _inventory = null;
    }

    [Test]
    public void AddItem_IncreasesCount()
    {
        _inventory.Add(new Item("Sword"));
        Assert.AreEqual(1, _inventory.Count);
    }

    [Test]
    public void AddItem_WhenFull_ReturnsFalse()
    {
        for (int i = 0; i < 10; i++)
            _inventory.Add(new Item($"Item{i}"));

        bool result = _inventory.Add(new Item("Extra"));
        Assert.IsFalse(result);
    }
}
```

## Assembly Definition Setup

Tests need their own assembly definitions:

### Edit Mode Tests (`Tests/EditMode/MyGame.Tests.EditMode.asmdef`)
```json
{
    "name": "MyGame.Tests.EditMode",
    "references": ["MyGame.Runtime"],
    "includePlatforms": ["Editor"],
    "optionalUnityReferences": ["TestAssemblies"]
}
```

### Play Mode Tests (`Tests/PlayMode/MyGame.Tests.PlayMode.asmdef`)
```json
{
    "name": "MyGame.Tests.PlayMode",
    "references": ["MyGame.Runtime", "UnityEngine.TestRunner", "UnityEditor.TestRunner"],
    "includePlatforms": [],
    "optionalUnityReferences": ["TestAssemblies"]
}
```

## Mocking Patterns

Use interfaces and dependency injection to make code testable:

```csharp
public interface IAudioService
{
    void PlaySFX(string name);
}

public class PlayerCombat
{
    private readonly IAudioService _audio;

    public PlayerCombat(IAudioService audio)
    {
        _audio = audio;
    }

    public void Attack(IDamageable target)
    {
        target.TakeDamage(10);
        _audio.PlaySFX("sword_swing");
    }
}
```

For automated mocking, use NSubstitute:

```csharp
var audioMock = Substitute.For<IAudioService>();
var target = Substitute.For<IDamageable>();

var combat = new PlayerCombat(audioMock);
combat.Attack(target);

target.Received(1).TakeDamage(10);
audioMock.Received(1).PlaySFX("sword_swing");
```

## Running Tests

- **Test Runner Window**: Window > General > Test Runner
- **Command Line**: `Unity.exe -runTests -testResults results.xml -testPlatform EditMode`
- **CI Integration**: Use the `-batchmode -nographics` flags for headless test execution
