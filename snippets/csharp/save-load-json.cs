// Save/Load System using JSON
// Persist game data to disk using JsonUtility.
// For complex data (dictionaries, polymorphism), use Newtonsoft.Json instead.

using System.IO;
using UnityEngine;

namespace MyGame
{
    [System.Serializable]
    public class SaveData
    {
        public string PlayerName;
        public int Level;
        public float PlayTime;
        public Vector3 PlayerPosition;
        public int[] InventoryItemIds;
    }

    public static class SaveSystem
    {
        private static string SavePath => Path.Combine(Application.persistentDataPath, "save.json");

        public static void Save(SaveData data)
        {
            string json = JsonUtility.ToJson(data, prettyPrint: true);
            File.WriteAllText(SavePath, json);
            Debug.Log($"Game saved to {SavePath}");
        }

        public static SaveData Load()
        {
            if (!File.Exists(SavePath))
            {
                Debug.Log("No save file found, creating new save data");
                return new SaveData();
            }

            string json = File.ReadAllText(SavePath);
            return JsonUtility.FromJson<SaveData>(json);
        }

        public static bool SaveExists() => File.Exists(SavePath);

        public static void DeleteSave()
        {
            if (File.Exists(SavePath))
            {
                File.Delete(SavePath);
                Debug.Log("Save file deleted");
            }
        }
    }

    // Usage example
    public class GameSaveManager : MonoBehaviour
    {
        public void SaveGame()
        {
            var player = FindFirstObjectByType<PlayerController>();
            var data = new SaveData
            {
                PlayerName = "Player1",
                Level = 5,
                PlayTime = Time.time,
                PlayerPosition = player ? player.transform.position : Vector3.zero,
                InventoryItemIds = new[] { 1, 3, 7, 12 }
            };
            SaveSystem.Save(data);
        }

        public void LoadGame()
        {
            if (!SaveSystem.SaveExists()) return;

            SaveData data = SaveSystem.Load();
            Debug.Log($"Loaded: {data.PlayerName}, Level {data.Level}");
        }
    }
}
