---
title: Audio Systems
description: Audio implementation patterns including AudioSource, AudioMixer, spatial audio, and audio management.
globs: ["**/*.cs", "**/*.mixer"]
standards-version: 1.10.0
---

# Audio Systems

## Core Components

### AudioSource

The primary component for playing sounds:

```csharp
[SerializeField] private AudioSource _audioSource;
[SerializeField] private AudioClip _shootSound;

public void PlayShoot()
{
    // PlayOneShot allows overlapping sounds from the same source
    _audioSource.PlayOneShot(_shootSound, 0.8f);
}
```

Key properties:
- `clip`: The default AudioClip
- `volume`: 0.0 to 1.0
- `pitch`: Playback speed (1.0 = normal). Randomize slightly for variety: `Random.Range(0.9f, 1.1f)`
- `spatialBlend`: 0 = 2D (UI, music), 1 = 3D (world sounds)
- `loop`: Enable for ambient sounds and music

### AudioListener

Receives all audio in the scene. Rules:
- Exactly one active AudioListener per scene
- Usually attached to the main camera
- 3D sound positioning is relative to the AudioListener

## AudioMixer

AudioMixer provides professional audio routing, effects, and volume control.

### Groups

Create a hierarchy of mixer groups:
```
Master
|-- Music
|-- SFX
|   |-- Weapons
|   |-- Footsteps
|   |-- UI
|-- Ambient
|-- Voice
```

### Exposed Parameters

Expose mixer parameters for script control:

```csharp
[SerializeField] private AudioMixer _mixer;

public void SetMusicVolume(float normalizedValue)
{
    // Convert 0-1 slider to decibels (-80 to 0)
    float dB = normalizedValue > 0.001f
        ? Mathf.Log10(normalizedValue) * 20f
        : -80f;
    _mixer.SetFloat("MusicVolume", dB);
}
```

### Snapshots

Pre-configure mixer states for different game contexts:
- Default: normal gameplay mix
- Paused: duck SFX, lower music
- Underwater: low-pass filter on all groups
- Menu: music only, SFX muted

Transition between snapshots: `snapshot.TransitionTo(0.5f)`.

### Effects

Built-in mixer effects: Reverb, Echo, Chorus, Flange, Distortion, Low Pass, High Pass, Compressor.

## 3D Spatial Audio

Configure AudioSource for spatial audio:
- **Spatial Blend**: Set to 1.0 for full 3D positioning
- **Min/Max Distance**: Controls volume rolloff range
- **Rolloff**: Logarithmic (realistic), Linear (predictable), or Custom curve
- **Doppler Level**: Pitch shift for moving sources (0 = off)
- **Spread**: Stereo width at the listener (0 = point source, 360 = surround)

## Audio Pooling

For sounds that play frequently (footsteps, impacts, bullets):

```csharp
public class AudioPool : MonoBehaviour
{
    [SerializeField] private int _poolSize = 10;
    private AudioSource[] _sources;
    private int _nextIndex;

    private void Awake()
    {
        _sources = new AudioSource[_poolSize];
        for (int i = 0; i < _poolSize; i++)
        {
            _sources[i] = gameObject.AddComponent<AudioSource>();
            _sources[i].playOnAwake = false;
        }
    }

    public void Play(AudioClip clip, float volume = 1f)
    {
        _sources[_nextIndex].PlayOneShot(clip, volume);
        _nextIndex = (_nextIndex + 1) % _poolSize;
    }
}
```

## Music Management

### Crossfading

```csharp
private async Awaitable CrossfadeAsync(AudioSource from, AudioSource to, float duration)
{
    to.volume = 0f;
    to.Play();

    float elapsed = 0f;
    while (elapsed < duration)
    {
        elapsed += Time.deltaTime;
        float t = elapsed / duration;
        from.volume = 1f - t;
        to.volume = t;
        await Awaitable.NextFrameAsync();
    }

    from.Stop();
    from.volume = 1f;
}
```

### Layered Music

Play multiple tracks simultaneously and blend between them for adaptive music:
- Base layer: ambient melody (always playing)
- Action layer: percussion (fade in during combat)
- Tension layer: strings (fade in during stealth)

## AudioClip Loading

- **Decompress On Load**: Small, frequently used clips (UI clicks, footsteps). Fastest playback, uses more memory.
- **Compressed In Memory**: Medium clips (SFX). Good balance of memory and CPU.
- **Streaming**: Large clips (music, ambient loops). Low memory, slight CPU cost.

## Common AudioManager Pattern

See `snippets/csharp/singleton-pattern.cs` for the Singleton base. Build an AudioManager that centralizes playback, manages the mixer, and provides a simple API:

```csharp
AudioManager.Instance.PlaySFX("explosion");
AudioManager.Instance.PlayMusic("battle_theme");
AudioManager.Instance.SetMusicVolume(0.7f);
```
