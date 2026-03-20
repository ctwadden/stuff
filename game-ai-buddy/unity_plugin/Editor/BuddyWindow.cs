using UnityEngine;
using UnityEditor;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace GameAIBuddy
{
    /// <summary>
    /// Main Unity Editor window for Game AI Buddy.
    /// Open via: Window > Game AI Buddy
    /// </summary>
    public class BuddyWindow : EditorWindow
    {
        private string _prompt = "";
        private string _reply = "";
        private string _extractedCode = "";
        private string _statusMsg = "";
        private bool _isLoading = false;
        private bool _serverOnline = false;
        private bool _showCode = true;
        private bool _includeScreenshot = false;
        private Vector2 _scrollReply;
        private Vector2 _scrollCode;

        private static readonly GUIStyle _headerStyle = new GUIStyle(EditorStyles.boldLabel)
        {
            fontSize = 16,
            alignment = TextAnchor.MiddleCenter,
        };

        [MenuItem("Window/Game AI Buddy")]
        public static void OpenWindow()
        {
            var window = GetWindow<BuddyWindow>("AI Buddy");
            window.minSize = new Vector2(380, 500);
            window.CheckServerStatus();
        }

        private async void CheckServerStatus()
        {
            _serverOnline = await BuddyClient.CheckOnline();
            Repaint();
        }

        private void OnGUI()
        {
            // Header
            EditorGUILayout.Space(8);
            EditorGUILayout.LabelField("Game AI Buddy", _headerStyle);
            EditorGUILayout.LabelField("Unity AI Assistant", EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.Space(4);

            // Server status
            var statusColor = _serverOnline ? Color.green : Color.red;
            var statusText = _serverOnline ? "Server Online" : "Server Offline - run: python server/main.py";
            EditorGUI.DrawRect(EditorGUILayout.GetControlRect(false, 2), statusColor);
            EditorGUILayout.LabelField(statusText, EditorStyles.centeredGreyMiniLabel);

            if (GUILayout.Button("Check Server", GUILayout.Height(22)))
                CheckServerStatus();

            EditorGUILayout.Space(8);
            EditorGUILayout.Separator();
            EditorGUILayout.Space(4);

            // Prompt area
            EditorGUILayout.LabelField("Ask AI Buddy:", EditorStyles.boldLabel);
            _prompt = EditorGUILayout.TextArea(_prompt, GUILayout.Height(80));

            _includeScreenshot = EditorGUILayout.Toggle("Send Screenshot", _includeScreenshot);

            EditorGUILayout.BeginHorizontal();
            GUI.enabled = !_isLoading && _serverOnline;
            if (GUILayout.Button(_isLoading ? "Thinking..." : "Ask Buddy", GUILayout.Height(32)))
                _ = SendPrompt();
            GUI.enabled = true;
            if (GUILayout.Button("Clear", GUILayout.Width(60), GUILayout.Height(32)))
                ClearAll();
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space(8);

            // Reply
            if (!string.IsNullOrEmpty(_reply))
            {
                EditorGUILayout.LabelField("Buddy says:", EditorStyles.boldLabel);
                _scrollReply = EditorGUILayout.BeginScrollView(_scrollReply, GUILayout.Height(150));
                EditorGUILayout.TextArea(_reply, EditorStyles.wordWrappedLabel);
                EditorGUILayout.EndScrollView();
            }

            // Code block
            if (!string.IsNullOrEmpty(_extractedCode))
            {
                EditorGUILayout.Space(4);
                _showCode = EditorGUILayout.Foldout(_showCode, "Generated C# Code", true, EditorStyles.foldoutHeader);
                if (_showCode)
                {
                    _scrollCode = EditorGUILayout.BeginScrollView(_scrollCode, GUILayout.Height(120));
                    EditorGUILayout.TextArea(_extractedCode, EditorStyles.wordWrappedMiniLabel);
                    EditorGUILayout.EndScrollView();
                }

                EditorGUILayout.Space(4);
                if (GUILayout.Button("Execute in Unity", GUILayout.Height(32)))
                    ExecuteCode(_extractedCode);
            }

            // Status
            if (!string.IsNullOrEmpty(_statusMsg))
            {
                EditorGUILayout.HelpBox(_statusMsg, MessageType.Info);
            }
        }

        private async Task SendPrompt()
        {
            if (string.IsNullOrWhiteSpace(_prompt)) return;

            _isLoading = true;
            _reply = "Thinking...";
            _extractedCode = "";
            _statusMsg = "";
            Repaint();

            try
            {
                var response = await BuddyClient.Ask(_prompt, _includeScreenshot);
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

        private void ExecuteCode(string code)
        {
            // For Unity, we write the code to a temp script and provide instructions
            // Full runtime compilation requires Roslyn which is available in Unity 2021+
            string tempPath = "Assets/BuddyTemp_Generated.cs";
            string wrapped = $@"// Auto-generated by Game AI Buddy - review before using in production
using UnityEngine;
using UnityEditor;

[InitializeOnLoad]
public class BuddyGenerated
{{
    static BuddyGenerated()
    {{
        EditorApplication.delayCall += Run;
    }}

    static void Run()
    {{
        {code}
        Debug.Log(""[Buddy] Generated code executed."");
    }}
}}";
            System.IO.File.WriteAllText(tempPath, wrapped);
            AssetDatabase.Refresh();
            _statusMsg = $"Code written to {tempPath} - Unity will recompile and execute it automatically.";
            Repaint();
        }

        private static string ExtractCSharpCode(string text)
        {
            var match = Regex.Match(text, @"```csharp\s*([\s\S]*?)```");
            if (match.Success) return match.Groups[1].Value.Trim();
            match = Regex.Match(text, @"```cs\s*([\s\S]*?)```");
            if (match.Success) return match.Groups[1].Value.Trim();
            return "";
        }

        private void ClearAll()
        {
            _prompt = "";
            _reply = "";
            _extractedCode = "";
            _statusMsg = "";
        }
    }
}
