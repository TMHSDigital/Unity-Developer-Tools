using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Audio;
using UnityEngine.UIElements;

namespace UIMenuSystem
{
    public class SettingsManager : MonoBehaviour
    {
        [SerializeField] private UIDocument _document;
        [SerializeField] private AudioMixer _audioMixer;

        // Exposed AudioMixer parameter names (right-click a volume in the mixer > Expose)
        private const string MasterVolumeParam = "MasterVolume";
        private const string MusicVolumeParam = "MusicVolume";
        private const string SfxVolumeParam = "SfxVolume";

        private const string QualityKey = "QualityLevel";
        private const string FullscreenKey = "Fullscreen";
        private const float DefaultVolume = 0.8f;

        private Slider _masterVolume;
        private Slider _musicVolume;
        private Slider _sfxVolume;
        private DropdownField _qualityDropdown;
        private Toggle _fullscreenToggle;

        private void OnEnable()
        {
            var root = _document.rootVisualElement;

            _masterVolume = root.Q<Slider>("master-volume");
            _musicVolume = root.Q<Slider>("music-volume");
            _sfxVolume = root.Q<Slider>("sfx-volume");
            _qualityDropdown = root.Q<DropdownField>("quality-dropdown");
            _fullscreenToggle = root.Q<Toggle>("fullscreen-toggle");

            _qualityDropdown.choices = new List<string>(QualitySettings.names);

            _masterVolume.RegisterValueChangedCallback(OnMasterVolumeChanged);
            _musicVolume.RegisterValueChangedCallback(OnMusicVolumeChanged);
            _sfxVolume.RegisterValueChangedCallback(OnSfxVolumeChanged);
            _qualityDropdown.RegisterValueChangedCallback(OnQualityChanged);
            _fullscreenToggle.RegisterValueChangedCallback(OnFullscreenChanged);
        }

        private void OnDisable()
        {
            _masterVolume.UnregisterValueChangedCallback(OnMasterVolumeChanged);
            _musicVolume.UnregisterValueChangedCallback(OnMusicVolumeChanged);
            _sfxVolume.UnregisterValueChangedCallback(OnSfxVolumeChanged);
            _qualityDropdown.UnregisterValueChangedCallback(OnQualityChanged);
            _fullscreenToggle.UnregisterValueChangedCallback(OnFullscreenChanged);
        }

        // AudioMixer.SetFloat has no effect in Awake/OnEnable, so saved settings are applied in Start
        private void Start()
        {
            LoadAndApplySettings();
        }

        private void OnMasterVolumeChanged(ChangeEvent<float> e) => SetVolume(MasterVolumeParam, e.newValue);
        private void OnMusicVolumeChanged(ChangeEvent<float> e) => SetVolume(MusicVolumeParam, e.newValue);
        private void OnSfxVolumeChanged(ChangeEvent<float> e) => SetVolume(SfxVolumeParam, e.newValue);
        private void OnQualityChanged(ChangeEvent<string> e) => SetQuality(_qualityDropdown.index);
        private void OnFullscreenChanged(ChangeEvent<bool> e) => SetFullscreen(e.newValue);

        private void SetVolume(string parameter, float normalizedValue)
        {
            ApplyVolume(parameter, normalizedValue);
            PlayerPrefs.SetFloat(parameter, normalizedValue);
        }

        private void ApplyVolume(string parameter, float normalizedValue)
        {
            float dB = normalizedValue > 0.001f ? Mathf.Log10(normalizedValue) * 20f : -80f;
            _audioMixer.SetFloat(parameter, dB);
        }

        private void SetQuality(int index)
        {
            if (index < 0 || index >= QualitySettings.names.Length)
                return;

            QualitySettings.SetQualityLevel(index);
            PlayerPrefs.SetInt(QualityKey, index);
        }

        private void SetFullscreen(bool isFullscreen)
        {
            Screen.fullScreen = isFullscreen;
            PlayerPrefs.SetInt(FullscreenKey, isFullscreen ? 1 : 0);
        }

        private void LoadAndApplySettings()
        {
            LoadVolume(_masterVolume, MasterVolumeParam);
            LoadVolume(_musicVolume, MusicVolumeParam);
            LoadVolume(_sfxVolume, SfxVolumeParam);

            int quality = PlayerPrefs.GetInt(QualityKey, QualitySettings.GetQualityLevel());
            quality = Mathf.Clamp(quality, 0, QualitySettings.names.Length - 1);
            QualitySettings.SetQualityLevel(quality);
            _qualityDropdown.SetValueWithoutNotify(QualitySettings.names[quality]);

            bool fullscreen = PlayerPrefs.GetInt(FullscreenKey, Screen.fullScreen ? 1 : 0) == 1;
            Screen.fullScreen = fullscreen;
            _fullscreenToggle.SetValueWithoutNotify(fullscreen);
        }

        private void LoadVolume(Slider slider, string parameter)
        {
            float value = PlayerPrefs.GetFloat(parameter, DefaultVolume);
            slider.SetValueWithoutNotify(value);
            ApplyVolume(parameter, value);
        }
    }
}
