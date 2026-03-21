using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine.Networking;

namespace GameAIBuddy
{
    /// <summary>
    /// Game Mechanics window — AI-generated code + direct-create buttons for
    /// animations, particle systems, and common game mechanic scripts.
    /// Open via: Window → Game AI Buddy → Mechanics
    /// </summary>
    public class MechanicsWindow : EditorWindow
    {
        // -----------------------------------------------------------------------
        //  Window setup
        // -----------------------------------------------------------------------

        [MenuItem("Window/Game AI Buddy/Mechanics", priority = 2)]
        public static void Open()
        {
            var win = GetWindow<MechanicsWindow>("Buddy: Mechanics");
            win.minSize = new Vector2(380, 580);
            win.Show();
        }

        // -----------------------------------------------------------------------
        //  State
        // -----------------------------------------------------------------------

        private enum Tab { Player, Combat, Animation, Particles, Systems, UI, Camera }
        private Tab _activeTab = Tab.Animation;

        private bool _teachMode;
        private string _customReq = "";
        private string _aiOutput  = "";
        private bool   _waiting;
        private string _statusMsg = "";
        private Color  _statusColor = Color.white;

        private Vector2 _scrollOutput;
        private Vector2 _scrollMain;

        // Particle color picker
        private Color _auraColor = new Color(0.4f, 0.2f, 1f);

        // Server URL (shared with main BuddyWindow)
        private string ServerUrl => BuddyPrefs.ServerUrl;

        // -----------------------------------------------------------------------
        //  Styles (lazily created)
        // -----------------------------------------------------------------------

        private GUIStyle _headerStyle;
        private GUIStyle _subHeaderStyle;
        private GUIStyle _codeStyle;
        private GUIStyle _btnMechanic;
        private GUIStyle _btnCreate;
        private GUIStyle _tabActive;
        private GUIStyle _tabInactive;
        private bool _stylesReady;

        private void EnsureStyles()
        {
            if (_stylesReady) return;

            _headerStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 14,
                normal = { textColor = new Color(0.9f, 0.85f, 1f) }
            };

            _subHeaderStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 11,
                normal = { textColor = new Color(0.7f, 0.9f, 1f) }
            };

            _codeStyle = new GUIStyle(EditorStyles.textArea)
            {
                font = (Font)Resources.Load("Fonts/RobotoMono") ?? EditorStyles.textArea.font,
                wordWrap = true,
                fontSize = 11,
                normal = { textColor = new Color(0.85f, 1f, 0.85f), background = MakeTex(2, 2, new Color(0.1f, 0.12f, 0.1f)) }
            };

            _btnMechanic = new GUIStyle(GUI.skin.button)
            {
                alignment = TextAnchor.MiddleLeft,
                padding = new RectOffset(10, 6, 5, 5),
                fontSize = 11
            };

            _btnCreate = new GUIStyle(GUI.skin.button)
            {
                fontSize = 11,
                fontStyle = FontStyle.Bold,
                normal   = { textColor = Color.black, background = MakeTex(2, 2, new Color(0.4f, 0.9f, 0.4f)) },
                hover    = { textColor = Color.black, background = MakeTex(2, 2, new Color(0.5f, 1f, 0.5f)) },
                active   = { textColor = Color.black, background = MakeTex(2, 2, new Color(0.3f, 0.7f, 0.3f)) }
            };

            _tabActive = new GUIStyle(EditorStyles.miniButtonMid)
            {
                fontStyle = FontStyle.Bold,
                normal = { textColor = Color.white, background = MakeTex(2, 2, new Color(0.25f, 0.45f, 0.65f)) }
            };
            _tabInactive = new GUIStyle(EditorStyles.miniButtonMid);

            _stylesReady = true;
        }

        // -----------------------------------------------------------------------
        //  OnGUI
        // -----------------------------------------------------------------------

        private void OnGUI()
        {
            EnsureStyles();
            _scrollMain = EditorGUILayout.BeginScrollView(_scrollMain);

            DrawHeader();
            EditorGUILayout.Space(4);
            DrawTabs();
            EditorGUILayout.Space(6);

            switch (_activeTab)
            {
                case Tab.Player:     DrawPlayerTab();     break;
                case Tab.Combat:     DrawCombatTab();     break;
                case Tab.Animation:  DrawAnimationTab();  break;
                case Tab.Particles:  DrawParticlesTab();  break;
                case Tab.Systems:    DrawSystemsTab();    break;
                case Tab.UI:         DrawUITab();         break;
                case Tab.Camera:     DrawCameraTab();     break;
            }

            EditorGUILayout.Space(6);
            DrawCustomRequest();
            EditorGUILayout.Space(4);
            DrawOutputArea();

            EditorGUILayout.EndScrollView();
        }

        // -----------------------------------------------------------------------
        //  Header
        // -----------------------------------------------------------------------

        private void DrawHeader()
        {
            EditorGUILayout.Space(6);
            EditorGUILayout.BeginHorizontal();
            GUILayout.Label("⚙  Game Mechanics", _headerStyle);
            GUILayout.FlexibleSpace();
            bool newTeach = GUILayout.Toggle(_teachMode, " Teach Mode", GUILayout.Width(100));
            if (newTeach != _teachMode) { _teachMode = newTeach; _aiOutput = ""; }
            EditorGUILayout.EndHorizontal();

            if (_teachMode)
            {
                EditorGUILayout.HelpBox("Teach Mode ON — AI will explain concepts before generating code.", MessageType.Info);
            }
        }

        // -----------------------------------------------------------------------
        //  Tab bar
        // -----------------------------------------------------------------------

        private void DrawTabs()
        {
            EditorGUILayout.BeginHorizontal();
            foreach (Tab t in Enum.GetValues(typeof(Tab)))
            {
                var style = t == _activeTab ? _tabActive : _tabInactive;
                if (GUILayout.Button(t.ToString(), style))
                    _activeTab = t;
            }
            EditorGUILayout.EndHorizontal();
        }

        // -----------------------------------------------------------------------
        //  Player tab
        // -----------------------------------------------------------------------

        private void DrawPlayerTab()
        {
            Label("Player Movement");
            MechanicBtn("Third-Person Controller",  "player.third_person");
            MechanicBtn("First-Person Controller",  "player.first_person");
            MechanicBtn("Top-Down Controller",      "player.top_down");
            MechanicBtn("Dash / Dodge",             "player.dash");
            MechanicBtn("Wall Run",                 "player.wall_run");
            MechanicBtn("Swimming",                 "player.swimming");
        }

        // -----------------------------------------------------------------------
        //  Combat tab
        // -----------------------------------------------------------------------

        private void DrawCombatTab()
        {
            Label("Combat & AI");
            MechanicBtn("Health System",            "combat.health");
            MechanicBtn("Melee Attack (Combo)",     "combat.melee");
            MechanicBtn("Ranged Weapon",            "combat.ranged");
            MechanicBtn("Area of Effect Damage",    "combat.area_damage");
            MechanicBtn("Enemy AI (State Machine)", "combat.enemy_ai");
        }

        // -----------------------------------------------------------------------
        //  Animation tab  — with direct-create buttons
        // -----------------------------------------------------------------------

        private void DrawAnimationTab()
        {
            Label("AI Code Generation");
            MechanicBtn("Animator Controller Setup (code)", "animation.setup_controller");
            MechanicBtn("2D Blend Tree (8-direction)",      "animation.blend_tree");
            MechanicBtn("Animator Driver Script",           "animation.animator_script");

            EditorGUILayout.Space(10);
            Label("Create Directly in Project");
            EditorGUILayout.HelpBox(
                "These buttons create .controller assets in Assets/Animations/ right now — no AI call needed.",
                MessageType.None);

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Create Player Animator", _btnCreate))
                CreateAndPing(() => AnimationHelper.CreateCharacterController("PlayerAnimator"));
            if (GUILayout.Button("Create Enemy Animator", _btnCreate))
                CreateAndPing(() => AnimationHelper.CreateEnemyController("EnemyAnimator"));
            EditorGUILayout.EndHorizontal();

            // Clip assignment utility
            EditorGUILayout.Space(8);
            Label("Assign Clip to State");
            EditorGUILayout.HelpBox(
                "Drag an AnimatorController and AnimationClip into Project view, then fill out below.",
                MessageType.None);

            _clipController = (AnimatorController)EditorGUILayout.ObjectField(
                "Controller", _clipController, typeof(AnimatorController), false);
            _clipStateName  = EditorGUILayout.TextField("State Name", _clipStateName);
            _clipLayerName  = EditorGUILayout.TextField("Layer Name", _clipLayerName);
            _clipClip       = (AnimationClip)EditorGUILayout.ObjectField(
                "Clip", _clipClip, typeof(AnimationClip), false);

            EditorGUI.BeginDisabledGroup(_clipController == null || _clipClip == null || string.IsNullOrEmpty(_clipStateName));
            if (GUILayout.Button("Assign Clip", _btnCreate))
                AnimationHelper.AssignClipToState(_clipController, _clipLayerName, _clipStateName, _clipClip);
            EditorGUI.EndDisabledGroup();
        }

        // drag fields for clip assignment
        private AnimatorController _clipController;
        private AnimationClip _clipClip;
        private string _clipStateName = "Idle";
        private string _clipLayerName = "Base Layer";

        // -----------------------------------------------------------------------
        //  Particles tab  — with direct-create buttons
        // -----------------------------------------------------------------------

        private void DrawParticlesTab()
        {
            Label("AI Code Generation");
            MechanicBtn("Fire Effect (code)",        "particles.fire");
            MechanicBtn("Explosion System (code)",   "particles.explosion");
            MechanicBtn("Magic Aura (code)",         "particles.magic_aura");
            MechanicBtn("Blood / Hit Impact (code)", "particles.blood_hit");
            MechanicBtn("Weather System (code)",     "particles.weather");

            EditorGUILayout.Space(10);
            Label("Create Directly in Scene");
            EditorGUILayout.HelpBox(
                "Creates particle systems attached to the selected GameObject (or scene root).",
                MessageType.None);

            var sel = Selection.activeTransform;
            string parentName = sel ? $"child of '{sel.name}'" : "scene root";
            EditorGUILayout.LabelField($"Parent: {parentName}", EditorStyles.miniLabel);

            // Fire
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Create Fire", _btnCreate))
                CreateAndPing(() => ParticlePresets.CreateFire("FireEffect", sel));
            if (GUILayout.Button("Create Footstep Dust", _btnCreate))
                CreateAndPing(() => ParticlePresets.CreateFootstepDust());
            EditorGUILayout.EndHorizontal();

            // Explosion
            if (GUILayout.Button("Create Explosion (at scene origin)", _btnCreate))
                CreateAndPing(() => ParticlePresets.CreateExplosion(Vector3.zero, 1f));

            // Magic aura with color picker
            EditorGUILayout.BeginHorizontal();
            _auraColor = EditorGUILayout.ColorField("Aura Color", _auraColor);
            if (GUILayout.Button("Create Magic Aura", _btnCreate, GUILayout.Width(130)))
                CreateAndPing(() => ParticlePresets.CreateMagicAura(_auraColor, sel));
            EditorGUILayout.EndHorizontal();

            // Rain
            EditorGUILayout.BeginHorizontal();
            _rainIntensity = EditorGUILayout.Slider("Rain Intensity", _rainIntensity, 0.1f, 3f);
            if (GUILayout.Button("Create Rain", _btnCreate, GUILayout.Width(100)))
                CreateAndPing(() => ParticlePresets.CreateRain(_rainIntensity));
            EditorGUILayout.EndHorizontal();

            // Level up
            if (GUILayout.Button("Create Level-Up Effect", _btnCreate))
                CreateAndPing(() => ParticlePresets.CreateLevelUpEffect(sel));
        }

        private float _rainIntensity = 1f;

        // -----------------------------------------------------------------------
        //  Systems tab
        // -----------------------------------------------------------------------

        private void DrawSystemsTab()
        {
            Label("Game Systems");
            MechanicBtn("Inventory System",       "systems.inventory");
            MechanicBtn("Save / Load System",     "systems.save_load");
            MechanicBtn("Dialogue System",        "systems.dialogue");
            MechanicBtn("Quest System",           "systems.quest");
            MechanicBtn("Object Pooling",         "systems.object_pooling");
        }

        // -----------------------------------------------------------------------
        //  UI tab
        // -----------------------------------------------------------------------

        private void DrawUITab()
        {
            Label("UI");
            MechanicBtn("Health Bar (animated)",  "ui.health_bar");
            MechanicBtn("Minimap System",         "ui.minimap");
        }

        // -----------------------------------------------------------------------
        //  Camera tab
        // -----------------------------------------------------------------------

        private void DrawCameraTab()
        {
            Label("Camera");
            MechanicBtn("Camera Shake (Trauma)",          "camera.shake");
            MechanicBtn("Third-Person Follow Camera",     "camera.third_person_follow");
        }

        // -----------------------------------------------------------------------
        //  Custom request field
        // -----------------------------------------------------------------------

        private void DrawCustomRequest()
        {
            EditorGUILayout.LabelField("Custom requirements (appended to next request)", EditorStyles.miniLabel);
            _customReq = EditorGUILayout.TextArea(_customReq, GUILayout.Height(40));
        }

        // -----------------------------------------------------------------------
        //  Output area
        // -----------------------------------------------------------------------

        private void DrawOutputArea()
        {
            if (_waiting)
            {
                EditorGUILayout.HelpBox("Generating… this may take a few seconds.", MessageType.None);
                return;
            }

            if (!string.IsNullOrEmpty(_statusMsg))
            {
                var prev = GUI.color;
                GUI.color = _statusColor;
                EditorGUILayout.LabelField(_statusMsg, EditorStyles.miniLabel);
                GUI.color = prev;
            }

            if (string.IsNullOrEmpty(_aiOutput)) return;

            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Generated Code", _subHeaderStyle);
            if (GUILayout.Button("Copy", GUILayout.Width(60)))
            {
                EditorGUIUtility.systemCopyBuffer = _aiOutput;
                Status("Copied to clipboard!", Color.green);
            }
            if (GUILayout.Button("Clear", GUILayout.Width(55)))
                _aiOutput = "";
            EditorGUILayout.EndHorizontal();

            _scrollOutput = EditorGUILayout.BeginScrollView(_scrollOutput, GUILayout.Height(300));
            EditorGUILayout.TextArea(_aiOutput, _codeStyle, GUILayout.ExpandHeight(true));
            EditorGUILayout.EndScrollView();
        }

        // -----------------------------------------------------------------------
        //  Helpers
        // -----------------------------------------------------------------------

        private void Label(string text)
        {
            EditorGUILayout.Space(4);
            EditorGUILayout.LabelField(text, _subHeaderStyle);
        }

        /// <summary>Draws a button that fires an AI mechanics request.</summary>
        private void MechanicBtn(string label, string mechanicKey)
        {
            EditorGUI.BeginDisabledGroup(_waiting);
            if (GUILayout.Button("  " + label, _btnMechanic))
                _ = RequestMechanic(mechanicKey);
            EditorGUI.EndDisabledGroup();
        }

        /// <summary>Wraps a create call in Undo + ping the result.</summary>
        private void CreateAndPing(Func<GameObject> creator)
        {
            var go = creator();
            if (go == null) return;
            Undo.RegisterCreatedObjectUndo(go, $"Create {go.name}");
            Selection.activeGameObject = go;
            EditorGUIUtility.PingObject(go);
            Status($"Created '{go.name}'", Color.green);
        }

        private void CreateAndPing(Func<UnityEditor.Animations.AnimatorController> creator)
        {
            var ac = creator();
            if (ac == null) return;
            Selection.activeObject = ac;
            EditorGUIUtility.PingObject(ac);
            Status($"Created '{ac.name}'", Color.green);
        }

        private void Status(string msg, Color col)
        {
            _statusMsg   = msg;
            _statusColor = col;
            Repaint();
        }

        // -----------------------------------------------------------------------
        //  Server request
        // -----------------------------------------------------------------------

        private async Task RequestMechanic(string key)
        {
            if (string.IsNullOrEmpty(ServerUrl))
            {
                Status("Server URL not set — open Window > Game AI Buddy > Buddy first.", Color.red);
                return;
            }

            _waiting  = true;
            _aiOutput = "";
            Status("Requesting…", Color.yellow);
            Repaint();

            try
            {
                string json = BuildJson(key, _customReq, _teachMode ? "teach" : "do");
                string result = await PostJson(ServerUrl.TrimEnd('/') + "/mechanics", json);

                if (result == null)
                {
                    Status("Server error — is the server running?", Color.red);
                }
                else
                {
                    _aiOutput = ParseReply(result);
                    Status($"Done ({key})", Color.green);
                }
            }
            catch (Exception ex)
            {
                Status($"Error: {ex.Message}", Color.red);
                Debug.LogException(ex);
            }
            finally
            {
                _waiting = false;
                Repaint();
            }
        }

        private static string BuildJson(string mechanic, string custom, string mode)
        {
            var sb = new StringBuilder();
            sb.Append("{");
            sb.Append($"\"mechanic\":{JsonString(mechanic)}");
            if (!string.IsNullOrEmpty(custom))
                sb.Append($",\"custom\":{JsonString(custom)}");
            sb.Append($",\"mode\":{JsonString(mode)}");
            sb.Append("}");
            return sb.ToString();
        }

        private static string JsonString(string s)
            => "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n") + "\"";

        private static async Task<string> PostJson(string url, string json)
        {
            byte[] body = Encoding.UTF8.GetBytes(json);
            using var req = new UnityWebRequest(url, "POST");
            req.uploadHandler   = new UploadHandlerRaw(body);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");

            var op = req.SendWebRequest();
            while (!op.isDone) await Task.Yield();

            if (req.result != UnityWebRequest.Result.Success) return null;
            return req.downloadHandler.text;
        }

        private static string ParseReply(string json)
        {
            // Simple parse — pull out "reply" field value
            int idx = json.IndexOf("\"reply\"");
            if (idx < 0) return json;
            int colon = json.IndexOf(':', idx);
            int start = json.IndexOf('"', colon + 1) + 1;
            int end   = start;
            while (end < json.Length)
            {
                if (json[end] == '\\') { end += 2; continue; }
                if (json[end] == '"') break;
                end++;
            }
            return json.Substring(start, end - start)
                       .Replace("\\n", "\n")
                       .Replace("\\t", "\t")
                       .Replace("\\\"", "\"")
                       .Replace("\\\\", "\\");
        }

        private static Texture2D MakeTex(int w, int h, Color col)
        {
            var pix = new Color[w * h];
            for (int i = 0; i < pix.Length; i++) pix[i] = col;
            var tex = new Texture2D(w, h);
            tex.SetPixels(pix);
            tex.Apply();
            return tex;
        }
    }

    // -----------------------------------------------------------------------
    //  Thin shared prefs wrapper (reuses BuddyWindow's saved URL)
    // -----------------------------------------------------------------------

    internal static class BuddyPrefs
    {
        private const string Key = "GameAIBuddy_ServerUrl";
        public static string ServerUrl
        {
            get => EditorPrefs.GetString(Key, "http://localhost:8000");
            set => EditorPrefs.SetString(Key, value);
        }
    }
}
