using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;

namespace UIMenuSystem
{
    [RequireComponent(typeof(UIDocument))]
    public class MenuManager : MonoBehaviour
    {
        [SerializeField] private string _gameSceneName = "Game";

        private UIDocument _document;
        private VisualElement _mainMenu;
        private VisualElement _settingsPanel;
        private Button _playButton;
        private Button _settingsButton;
        private Button _quitButton;
        private Button _backButton;

        private void Awake()
        {
            _document = GetComponent<UIDocument>();
        }

        private void OnEnable()
        {
            var root = _document.rootVisualElement;

            _mainMenu = root.Q<VisualElement>("main-menu");
            _settingsPanel = root.Q<VisualElement>("settings-panel");

            _playButton = root.Q<Button>("play-button");
            _settingsButton = root.Q<Button>("settings-button");
            _quitButton = root.Q<Button>("quit-button");
            _backButton = root.Q<Button>("back-button");

            _playButton.clicked += OnPlayClicked;
            _settingsButton.clicked += OnSettingsClicked;
            _quitButton.clicked += OnQuitClicked;
            _backButton.clicked += OnBackClicked;

            ShowMainMenu();
        }

        private void OnDisable()
        {
            _playButton.clicked -= OnPlayClicked;
            _settingsButton.clicked -= OnSettingsClicked;
            _quitButton.clicked -= OnQuitClicked;
            _backButton.clicked -= OnBackClicked;
        }

        private void OnPlayClicked()
        {
            SceneManager.LoadScene(_gameSceneName);
        }

        private void OnSettingsClicked()
        {
            _mainMenu.style.display = DisplayStyle.None;
            _settingsPanel.style.display = DisplayStyle.Flex;
        }

        private void OnBackClicked()
        {
            ShowMainMenu();
        }

        private void OnQuitClicked()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        private void ShowMainMenu()
        {
            _mainMenu.style.display = DisplayStyle.Flex;
            _settingsPanel.style.display = DisplayStyle.None;
        }
    }
}
