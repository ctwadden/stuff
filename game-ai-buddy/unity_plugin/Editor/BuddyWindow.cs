using UnityEngine;
using UnityEditor;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.IO;

namespace GameAIBuddy
{
    /// <summary>
    /// Main Unity Editor window for Game AI Buddy v2.
    /// Window > Game AI Buddy
    /// Features: Do/Teach mode | Vision | PCG Biome | Terrain | Asset management
    /// </summary>
    public class BuddyWindow : EditorWindow
    {
        // State
        private string _prompt = "";
        private string _reply = "";
        private string _extractedCode = "";
        private string _statusMsg = "";
        private bool _isLoading = false;
        private bool _serverOnline = false;
        private bool _includeScreenshot = false;
        private int _modeIndex = 0;           // 0=Do It, 1=Teach Me
        private int _tabIndex = 0;            // Chat | Biome | Terrain | Assets
        private Vector2 _scrollReply;
        private Vector2 _scrollCode;

        // Biome tab
        private int _biomeIndex = 0;
        private float _densityMultiplier = 1f;
        private bool _clearExisting = true;

        // Asset tab
        private string _oldAssetPath = "";
        private string _newAssetPath = "";

        private static readonly string[] ModeLabels = { "Do It (generate code)", "Teach Me (step-by-step)" };
        private static readonly string[] TabLabels  = { "Chat", "Biome / PCG", "Terrain", "Assets" };
        private static readonly string[] BiomeNames = { "forest", "desert", "mountain", "swamp", "coastal" };

        // Styles (initialised on first use)
        private GUIStyle _headerStyle;
        private GUIStyle _replyStyle;
        private GUIStyle _codeStyle;
        private bool _stylesInit = false;

        [MenuItem("Window/Game AI Buddy")]
        public static void OpenWindow()
        {
            var w = GetWindow<BuddyWindow>("AI Buddy");
            w.minSize = new Vector2(420, 600);
            w.CheckServer();
        }

        private void InitStyles()
        {
            if (_stylesInit) return;
            _headerStyle = new GUIStyle(EditorStyles.boldLabel) { fontSize = 16, alignment = TextAnchor.MiddleCenter };
            _replyStyle  = new GUIStyle(EditorStyles.wordWrappedLabel) { wordWrap = true };
            _codeStyle   = new GUIStyle(EditorStyles.wordWrappedMiniLabel) { fontStyle = FontStyle.Bold, wordWrap = true };
            _stylesInit = true;
        }

        private async void CheckServer()
        {
            _serverOnline = await BuddyClient.CheckOnline();
            Repaint();
        }

        private void OnGUI()
        {
            InitStyles();

            // Header
            EditorGUILayout.Space(6);
            EditorGUILayout.LabelField("Game AI Buddy", _headerStyle);
            EditorGUILayout.LabelField("Unity Editor AI Assistant", EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.Space(4);

            // Server status
            var statusColor = _serverOnline ? new Color(0.2f, 0.8f, 0.2f) : new Color(0.9f, 0.2f, 0.2f);
            var rect = EditorGUILayout.GetControlRect(false, 2);
            EditorGUI.DrawRect(rect, statusColor);

            var statusText = _serverOnline ? "Server Online" : "Server Offline — run start_server.bat / start_server.sh";
            EditorGUILayout.LabelField(statusText, EditorStyles.centeredGreyMiniLabel);

            if (GUILayout.Button("Check Server", GUILayout.Height(20)))
                CheckServer();

            EditorGUILayout.Space(4);

            // Mode toggle
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Mode:", GUILayout.Width(48));
            _modeIndex = GUILayout.Toolbar(_modeIndex, ModeLabels);
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space(4);

            // Tabs
            _tabIndex = GUILayout.Toolbar(_tabIndex, TabLabels);
            EditorGUILayout.Space(4);

            switch (_tabIndex)
            {
                case 0: DrawChatTab();    break;
                case 1: DrawBiomeTab();   break;
                case 2: DrawTerrainTab(); break;
                case 3: DrawAssetsTab();  break;
            }

            EditorGUILayout.Separator();
            DrawReplyArea();
        }

        // -----------------------------------------------------------------------
        //  Tabs
        // -----------------------------------------------------------------------

        private void DrawChatTab()
        {
            string hint = _modeIndex == 1
                ? "Ask Buddy to TEACH you — it will give step-by-step instructions:"
                : "Tell Buddy what to BUILD — it will generate C# code:";
            EditorGUILayout.LabelField(hint, EditorStyles.wordWrappedLabel);

            _prompt = EditorGUILayout.TextArea(_prompt, GUILayout.Height(80));
            _includeScreenshot = EditorGUILayout.Toggle("Include screenshot (vision)", _includeScreenshot);

            EditorGUILayout.BeginHorizontal();
            GUI.enabled = !_isLoading && _serverOnline;

            string btnLabel = _isLoading ? "Thinking..." : (_modeIndex == 1 ? "Teach Me" : "Ask Buddy");
            if (GUILayout.Button(btnLabel, GUILayout.Height(30)))
                _ = SendPrompt(_prompt);

            if (GUILayout.Button("See Screen", GUILayout.Height(30), GUILayout.Width(90)))
                _ = SeeScreen();

            GUI.enabled = true;
            if (GUILayout.Button("Clear", GUILayout.Height(30), GUILayout.Width(55)))
                ClearAll();

            EditorGUILayout.EndHorizontal();

            // Quick teach buttons
            if (_modeIndex == 1)
            {
                EditorGUILayout.Space(4);
                EditorGUILayout.LabelField("Quick tutorials:", EditorStyles.miniLabel);
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("Terrain basics")) _ = SendPrompt("Teach me how Unity terrain works - height, textures, foliage");
                if (GUILayout.Button("Lighting setup"))  _ = SendPrompt("Teach me how to set up lighting in Unity with URP/HDRP");
                EditorGUILayout.EndHorizontal();
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("Prefabs"))         _ = SendPrompt("Teach me how Unity prefabs work and when to use them");
                if (GUILayout.Button("Physics setup"))   _ = SendPrompt("Teach me how to add physics and colliders in Unity");
                EditorGUILayout.EndHorizontal();
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("Cinemachine"))     _ = SendPrompt("Teach me how to use Cinemachine for a third-person camera");
                if (GUILayout.Button("Shader Graph"))    _ = SendPrompt("Teach me the basics of Unity Shader Graph");
                EditorGUILayout.EndHorizontal();
            }
        }

        private void DrawBiomeTab()
        {
            EditorGUILayout.HelpBox(
                "Populate your terrain with a full biome. Assign your prefabs to PCGController biome layers, " +
                "then click Populate. The AI can generate the prefab-loading code for you.",
                MessageType.Info);

            EditorGUILayout.LabelField("Biome:", EditorStyles.boldLabel);
            _biomeIndex = EditorGUILayout.Popup(_biomeIndex, BiomeNames);

            EditorGUILayout.LabelField($"Density: {_densityMultiplier:F1}x");
            _densityMultiplier = EditorGUILayout.Slider(_densityMultiplier, 0.1f, 3f);

            _clearExisting = EditorGUILayout.Toggle("Clear existing buddy actors", _clearExisting);

            EditorGUILayout.Space(4);

            if (GUILayout.Button("Generate Prefab-Loading Code for this Biome", GUILayout.Height(26)))
            {
                string biome = BiomeNames[_biomeIndex];
                _ = SendPrompt(
                    $"Generate Unity C# Editor code to load prefabs from Resources and call PCGController.PopulateBiome " +
                    $"for the '{biome}' biome with density {_densityMultiplier:F1}. " +
                    $"Include Resources.LoadAll calls for common {biome} asset names."
                );
            }

            if (GUILayout.Button($"Clear All Buddy Actors", GUILayout.Height(26)))
            {
                PCGController.ClearBuddyActors();
                _statusMsg = "Cleared all buddy actors.";
                Repaint();
            }

            EditorGUILayout.Space(4);
            if (GUILayout.Button("Scene Summary", GUILayout.Height(22)))
            {
                _reply = PCGController.GetSceneSummary();
                Repaint();
            }
        }

        private void DrawTerrainTab()
        {
            EditorGUILayout.LabelField("Terrain Quick Actions:", EditorStyles.boldLabel);

            var terrain = Terrain.activeTerrain;
            if (terrain == null)
            {
                EditorGUILayout.HelpBox("No active terrain in scene. Create one first.", MessageType.Warning);
                if (GUILayout.Button("Generate Terrain Creation Code"))
                    _ = SendPrompt("Generate C# Editor code to create a Unity terrain with size 512x512 and realistic height settings");
            }
            else
            {
                EditorGUILayout.LabelField($"Active terrain: {terrain.name}", EditorStyles.miniLabel);

                if (GUILayout.Button("Add Mountains (noise)", GUILayout.Height(26)))
                    _ = SendPrompt("Generate C# Editor code to add mountainous noise to the active terrain using Perlin noise with peaks and valleys");

                if (GUILayout.Button("Flatten Terrain", GUILayout.Height(26)))
                {
                    TerrainController.Flatten(terrain);
                    _statusMsg = "Terrain flattened.";
                    Repaint();
                }

                if (GUILayout.Button("Add Noise (gentle hills)", GUILayout.Height(26)))
                {
                    TerrainController.AddNoise(terrain, scale: 80f, strength: 0.04f);
                    _statusMsg = "Added gentle hills.";
                    Repaint();
                }

                if (GUILayout.Button("Paint by Slope/Altitude", GUILayout.Height(26)))
                {
                    PCGController.PaintByRules(terrain);
                    _statusMsg = "Terrain painted.";
                    Repaint();
                }
            }

            EditorGUILayout.Space(4);
            EditorGUILayout.LabelField("Describe terrain changes:", EditorStyles.boldLabel);
            _prompt = EditorGUILayout.TextField(_prompt);
            if (GUILayout.Button("Ask AI for Terrain Code"))
                _ = SendPrompt(_prompt);
        }

        private void DrawAssetsTab()
        {
            EditorGUILayout.LabelField("Swap Prefabs:", EditorStyles.boldLabel);
            _oldAssetPath = EditorGUILayout.TextField("Old Prefab Path", _oldAssetPath);
            _newAssetPath = EditorGUILayout.TextField("New Prefab Path", _newAssetPath);

            if (GUILayout.Button("Generate Swap Code"))
                _ = SendPrompt($"Generate C# Editor code to swap all instances of prefab at '{_oldAssetPath}' with the prefab at '{_newAssetPath}'. Use PCGController.SwapPrefabs if available.");

            EditorGUILayout.Space(6);
            EditorGUILayout.LabelField("Asset scatter:", EditorStyles.boldLabel);

            if (GUILayout.Button("Scatter Trees on Flat Ground"))
                _ = SendPrompt("Generate C# code to scatter tree prefabs across the active terrain on slopes below 25 degrees. Use PCGController or TerrainController.ScatterObjects.");

            if (GUILayout.Button("Scatter Rocks on Slopes"))
                _ = SendPrompt("Generate C# code to scatter rock prefabs on the active terrain on slopes between 20 and 50 degrees.");

            if (GUILayout.Button("Scatter Buildings Along Road"))
                _ = SendPrompt("Generate C# code to scatter building prefabs in a line along the X axis of the terrain, evenly spaced.");
        }

        // -----------------------------------------------------------------------
        //  Reply area (shared across all tabs)
        // -----------------------------------------------------------------------

        private void DrawReplyArea()
        {
            if (!string.IsNullOrEmpty(_reply))
            {
                string replyLabel = _modeIndex == 1 ? "Buddy's Tutorial:" : "Buddy says:";
                EditorGUILayout.LabelField(replyLabel, EditorStyles.boldLabel);
                _scrollReply = EditorGUILayout.BeginScrollView(_scrollReply, GUILayout.Height(120));
                EditorGUILayout.SelectableLabel(_reply, _replyStyle, GUILayout.ExpandHeight(true));
                EditorGUILayout.EndScrollView();

                // Do-step buttons in teach mode
                if (_modeIndex == 1)
                {
                    var steps = Regex.Matches(_reply, @"Step\s+(\d+)", RegexOptions.IgnoreCase);
                    if (steps.Count > 0)
                    {
                        EditorGUILayout.LabelField("Do a step for me:", EditorStyles.miniLabel);
                        EditorGUILayout.BeginHorizontal();
                        foreach (System.Text.RegularExpressions.Match m in steps)
                        {
                            if (GUILayout.Button($"Step {m.Groups[1].Value}", GUILayout.Width(65)))
                                _ = SendPrompt($"Do step {m.Groups[1].Value} for me");
                        }
                        EditorGUILayout.EndHorizontal();
                    }
                }
            }

            if (!string.IsNullOrEmpty(_extractedCode))
            {
                EditorGUILayout.LabelField("Generated C# Code:", EditorStyles.boldLabel);
                _scrollCode = EditorGUILayout.BeginScrollView(_scrollCode, GUILayout.Height(90));
                EditorGUILayout.SelectableLabel(_extractedCode, _codeStyle, GUILayout.ExpandHeight(true));
                EditorGUILayout.EndScrollView();

                if (GUILayout.Button("Execute in Unity", GUILayout.Height(28)))
                    ExecuteCode(_extractedCode);
            }

            if (!string.IsNullOrEmpty(_statusMsg))
                EditorGUILayout.HelpBox(_statusMsg, MessageType.Info);
        }

        // -----------------------------------------------------------------------
        //  AI calls
        // -----------------------------------------------------------------------

        private string GetMode() => _modeIndex == 1 ? "teach" : "do";

        private async Task SendPrompt(string prompt)
        {
            if (string.IsNullOrWhiteSpace(prompt)) return;
            _isLoading = true;
            _reply = "Thinking...";
            _extractedCode = "";
            _statusMsg = "";
            Repaint();

            try
            {
                var response = await BuddyClient.Ask(prompt, _includeScreenshot);
                _reply = response.reply;
                _extractedCode = ExtractCSharpCode(response.reply);
            }
            catch (System.Exception ex)
            {
                _reply = $"Error: {ex.Message}";
            }

            _isLoading = false;
            Repaint();
        }

        private async Task SeeScreen()
        {
            string p = string.IsNullOrWhiteSpace(_prompt)
                ? "Look at my Unity Editor screen and tell me what I'm working on and what I should do next."
                : _prompt;
            await SendPrompt(p);
        }

        private void ExecuteCode(string code)
        {
            string tempPath = "Assets/BuddyGenerated.cs";
            string wrapped = $@"// Generated by Game AI Buddy — review before production use
using UnityEngine;
using UnityEditor;
using GameAIBuddy;

[InitializeOnLoad]
public class BuddyGenerated
{{
    static BuddyGenerated() {{ EditorApplication.delayCall += Run; }}
    static void Run()
    {{
        {code}
        Debug.Log(""[Buddy] Generated code executed."");
    }}
}}";
            File.WriteAllText(tempPath, wrapped);
            AssetDatabase.Refresh();
            _statusMsg = $"Code written to {tempPath} — Unity will recompile and execute automatically.";
            Repaint();
        }

        private void ClearAll()
        {
            _prompt = "";
            _reply = "";
            _extractedCode = "";
            _statusMsg = "";
        }

        private static string ExtractCSharpCode(string text)
        {
            var m = Regex.Match(text, @"```(?:csharp|cs)\s*([\s\S]*?)```");
            return m.Success ? m.Groups[1].Value.Trim() : "";
        }
    }
}
