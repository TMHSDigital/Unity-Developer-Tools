using UnityEngine;
using UnityEngine.Audio;
using UnityEngine.UIElements;

namespace UIMenuSystem
{
    public class SettingsManager : MonoBehaviour
    {
        [SerializeField] private UIDocument _document;
        [SerializeField] private AudioMixer _audioMixer;

        private Slider _masterVolume;
        private Slider _musicVolume;
        private Slider _sfxVolume;
        private DropdownField _qualityDropdown;
        private Toggle _fullscreenToggle;

        private const string MasterVolumeKey = "MasterVolume";
        private const string MusicVolumeKey = "MusicVolume";
        private const string SfxVolumeKey = "SfxVolume";
        private const string QualityKey = "QualityLevel";

        private void OnEnable()
        {
            var root = _document.rootVisualElement;

            _masterVolume = root.Q<Slider>("master-volume");
            _musicVolume = root.Q<Slider>("music-volume");
            _sfxVolume = root.Q<Slider>("sfx-volume");
            _qualityDropdown = root.Q<DropdownField>("quality-dropdown");
            _fullscreenToggle = root.Q<Toggle>("fullscreen-toggle");

            LoadSettings();

            _masterVolume.RegisterValueChangedCallback(e => SetVolume("MasterVolume", e.newValue));
            _musicVolume.RegisterValueChangedCallback(e => SetVolume("MusicVolume", e.newValue));
            _sfxVolume.RegisterValueChangedCallback(e => SetVolume("SfxVolume", e.newValue));
            _qualityDropdown.RegisterValueChangedCallback(e => SetQuality(e.newValue));
            _fullscreenToggle.RegisterValueChangedCallback(e => SetFullscreen(e.newValue));
        }

        private void SetVolume(string parameter, float normalizedValue)
        {
            float dB = normalizedValue > 0.001f ? Mathf.Log10(normalizedValue) * 20f : -80f;
            _audioMixer.SetFloat(parameter, dB);
            PlayerPrefs.SetFloat(parameter, normalizedValue);
        }

        private void SetQuality(string qualityName)
        {
            int index = System.Array.IndexOf(QualitySettings.names, qualityName);
            if (index >= 0)
            {
                QualitySettings.SetQualityLevel(index);
                PlayerPrefs.SetInt(QualityKey, index);
            }
        }

        private void SetFullscreen(bool isFullscreen)
        {
            Screen.fullScreen = isFullscreen;
        }

        private void LoadSettings()
        {
            _masterVolume.value = PlayerPrefs.GetFloat(MasterVolumeKey, 0.8f);
            _musicVolume.value = PlayerPrefs.GetFloat(MusicVolumeKey, 0.8f);
            _sfxVolume.value = PlayerPrefs.GetFloat(SfxVolumeKey, 0.8f);

            if (_qualityDropdown != null)
            {
                _qualityDropdown.choices = new System.Collections.Generic.List<string>(QualitySettings.names);
                int quality = PlayerPrefs.GetInt(QualityKey, QualitySettings.GetQualityLevel());
                _qualityDropdown.index = quality;
            }

            if (_fullscreenToggle != null)
            {
                _fullscreenToggle.value = Screen.fullScreen;
            }
        }
    }
}
