using UnityEngine;

namespace SOArchitecture
{
    // Concrete set asset. Create one per group you want to track (enemies, pickups, ...).
    // Add a subclass like this for any other type, e.g. RuntimeSet<Enemy>.
    [CreateAssetMenu(fileName = "New Transform Set", menuName = "Runtime Sets/Transform Set")]
    public class TransformRuntimeSet : RuntimeSet<Transform>
    {
    }
}
