using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using System.IO;

namespace GameAIBuddy
{
    /// <summary>
    /// Creates Animator Controllers and configures state machines in code.
    /// All methods are callable from AI-generated code or the Mechanics window.
    /// </summary>
    public static class AnimationHelper
    {
        private const string DefaultOutputPath = "Assets/Animations/";

        // -----------------------------------------------------------------------
        //  Animator Controller builders
        // -----------------------------------------------------------------------

        /// <summary>
        /// Create a full character animator controller with locomotion blend tree,
        /// jump, fall, attack, and death states — all wired up with transitions.
        /// </summary>
        public static AnimatorController CreateCharacterController(string assetName = "PlayerAnimator")
        {
            EnsureFolder(DefaultOutputPath);
            string path = $"{DefaultOutputPath}{assetName}.controller";

            var controller = AnimatorController.CreateAnimatorControllerAtPath(path);

            // --- Parameters ---
            controller.AddParameter("Speed",      AnimatorControllerParameterType.Float);
            controller.AddParameter("IsGrounded", AnimatorControllerParameterType.Bool);
            controller.AddParameter("Jump",       AnimatorControllerParameterType.Trigger);
            controller.AddParameter("Attack",     AnimatorControllerParameterType.Trigger);
            controller.AddParameter("Die",        AnimatorControllerParameterType.Trigger);
            controller.AddParameter("IsAiming",   AnimatorControllerParameterType.Bool);
            controller.AddParameter("MoveX",      AnimatorControllerParameterType.Float);
            controller.AddParameter("MoveZ",      AnimatorControllerParameterType.Float);

            var rootSM = controller.layers[0].stateMachine;

            // --- States ---
            var idle   = rootSM.AddState("Idle");
            var walk   = rootSM.AddState("Walk");
            var run    = rootSM.AddState("Run");
            var jump   = rootSM.AddState("Jump");
            var fall   = rootSM.AddState("Fall");
            var land   = rootSM.AddState("Land");
            var attack = rootSM.AddState("Attack");
            var die    = rootSM.AddState("Die");

            // Place states so the graph is readable
            idle.position   = new Vector3(0,   0,   0);
            walk.position   = new Vector3(250, 0,   0);
            run.position    = new Vector3(500, 0,   0);
            jump.position   = new Vector3(250, -150, 0);
            fall.position   = new Vector3(500, -150, 0);
            land.position   = new Vector3(250, -300, 0);
            attack.position = new Vector3(0,   -300, 0);
            die.position    = new Vector3(0,   -450, 0);

            rootSM.defaultState = idle;

            // --- Locomotion blend tree (replaces Idle/Walk/Run with one blend tree) ---
            AnimatorState locoState;
            var blendTree = CreateLocomotionBlendTree(controller, out locoState);
            locoState.position = new Vector3(-250, 0, 0);
            rootSM.defaultState = locoState;

            // --- Transitions ---

            // Loco → Jump
            AddTriggerTransition(locoState, jump, "Jump", hasExitTime: false);

            // Jump → Fall (after 0.4s)
            var jumpToFall = jump.AddTransition(fall);
            jumpToFall.hasExitTime = true;
            jumpToFall.exitTime = 0.4f;
            jumpToFall.duration = 0.1f;

            // Fall → Land (IsGrounded becomes true)
            var fallToLand = fall.AddTransition(land);
            fallToLand.hasExitTime = false;
            fallToLand.duration = 0.05f;
            fallToLand.AddCondition(AnimatorConditionMode.If, 0, "IsGrounded");

            // Land → Loco (after play)
            var landToLoco = land.AddTransition(locoState);
            landToLoco.hasExitTime = true;
            landToLoco.exitTime = 0.8f;
            landToLoco.duration = 0.2f;

            // Any → Attack
            var anyAttack = rootSM.AddAnyStateTransition(attack);
            anyAttack.AddCondition(AnimatorConditionMode.If, 0, "Attack");
            anyAttack.canTransitionToSelf = false;
            anyAttack.duration = 0.05f;
            anyAttack.hasExitTime = false;

            // Attack → Loco
            var attackToLoco = attack.AddTransition(locoState);
            attackToLoco.hasExitTime = true;
            attackToLoco.exitTime = 0.9f;
            attackToLoco.duration = 0.15f;

            // Any → Die
            var anyDie = rootSM.AddAnyStateTransition(die);
            anyDie.AddCondition(AnimatorConditionMode.If, 0, "Die");
            anyDie.canTransitionToSelf = false;
            anyDie.hasExitTime = false;
            anyDie.duration = 0.1f;

            // --- Upper body additive layer for aiming ---
            AddUpperBodyLayer(controller);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"[Buddy] Created animator controller: {path}");
            return controller;
        }

        private static BlendTree CreateLocomotionBlendTree(AnimatorController controller, out AnimatorState state)
        {
            BlendTree tree;
            state = controller.CreateBlendTreeInController("Locomotion", out tree);
            tree.blendType = BlendTreeType.Simple1D;
            tree.blendParameter = "Speed";
            tree.useAutomaticThresholds = false;

            tree.AddChild(null, 0f);   // Idle clip placeholder
            tree.AddChild(null, 0.5f); // Walk clip placeholder
            tree.AddChild(null, 1f);   // Run clip placeholder

            // Name the children descriptively
            var children = tree.children;
            if (children.Length >= 3)
            {
                children[0].directBlendParameter = "Speed"; // unused but needed
            }

            return tree;
        }

        private static void AddUpperBodyLayer(AnimatorController controller)
        {
            controller.AddLayer("UpperBody");
            var layers = controller.layers;
            int idx = layers.Length - 1;
            layers[idx].defaultWeight = 1f;
            layers[idx].blendingMode = AnimatorLayerBlendingMode.Additive;
            controller.layers = layers;
        }

        private static AnimatorStateTransition AddTriggerTransition(
            AnimatorState from, AnimatorState to, string triggerName, bool hasExitTime = false)
        {
            var t = from.AddTransition(to);
            t.hasExitTime = hasExitTime;
            t.duration = 0.05f;
            t.AddCondition(AnimatorConditionMode.If, 0, triggerName);
            return t;
        }

        // -----------------------------------------------------------------------
        //  Enemy AI controller
        // -----------------------------------------------------------------------

        public static AnimatorController CreateEnemyController(string assetName = "EnemyAnimator")
        {
            EnsureFolder(DefaultOutputPath);
            string path = $"{DefaultOutputPath}{assetName}.controller";
            var controller = AnimatorController.CreateAnimatorControllerAtPath(path);

            controller.AddParameter("Speed",    AnimatorControllerParameterType.Float);
            controller.AddParameter("Attack",   AnimatorControllerParameterType.Trigger);
            controller.AddParameter("Hurt",     AnimatorControllerParameterType.Trigger);
            controller.AddParameter("Die",      AnimatorControllerParameterType.Trigger);
            controller.AddParameter("IsAlert",  AnimatorControllerParameterType.Bool);

            var sm = controller.layers[0].stateMachine;

            var idle    = sm.AddState("Idle");
            var patrol  = sm.AddState("Patrol");
            var alert   = sm.AddState("Alert");
            var chase   = sm.AddState("Chase");
            var attack  = sm.AddState("Attack");
            var hurt    = sm.AddState("Hurt");
            var die     = sm.AddState("Die");

            idle.position   = new Vector3(0,    0,    0);
            patrol.position = new Vector3(250,  0,    0);
            alert.position  = new Vector3(125,  -150, 0);
            chase.position  = new Vector3(250,  -300, 0);
            attack.position = new Vector3(0,    -300, 0);
            hurt.position   = new Vector3(0,    -450, 0);
            die.position    = new Vector3(250,  -450, 0);

            sm.defaultState = idle;

            // Idle ↔ Patrol by Speed
            var idleToPatrol = idle.AddTransition(patrol);
            idleToPatrol.AddCondition(AnimatorConditionMode.Greater, 0.1f, "Speed");
            idleToPatrol.duration = 0.2f;

            var patrolToIdle = patrol.AddTransition(idle);
            patrolToIdle.AddCondition(AnimatorConditionMode.Less, 0.05f, "Speed");
            patrolToIdle.duration = 0.2f;

            // → Alert on IsAlert
            var idleToAlert = idle.AddTransition(alert);
            idleToAlert.AddCondition(AnimatorConditionMode.If, 0, "IsAlert");
            var patrolToAlert = patrol.AddTransition(alert);
            patrolToAlert.AddCondition(AnimatorConditionMode.If, 0, "IsAlert");

            // Alert → Chase by Speed
            var alertToChase = alert.AddTransition(chase);
            alertToChase.AddCondition(AnimatorConditionMode.Greater, 0.5f, "Speed");
            alertToChase.hasExitTime = true;
            alertToChase.exitTime = 0.8f;

            // Any → Attack, Hurt, Die
            var anyAttack = sm.AddAnyStateTransition(attack);
            anyAttack.AddCondition(AnimatorConditionMode.If, 0, "Attack");
            anyAttack.canTransitionToSelf = false;

            var anyHurt = sm.AddAnyStateTransition(hurt);
            anyHurt.AddCondition(AnimatorConditionMode.If, 0, "Hurt");
            anyHurt.canTransitionToSelf = false;

            var anyDie = sm.AddAnyStateTransition(die);
            anyDie.AddCondition(AnimatorConditionMode.If, 0, "Die");
            anyDie.canTransitionToSelf = false;

            // Attack/Hurt → back to chase
            var attackBack = attack.AddTransition(chase);
            attackBack.hasExitTime = true; attackBack.exitTime = 0.9f;

            var hurtBack = hurt.AddTransition(chase);
            hurtBack.hasExitTime = true; hurtBack.exitTime = 0.8f;

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"[Buddy] Created enemy animator controller: {path}");
            return controller;
        }

        // -----------------------------------------------------------------------
        //  Utility
        // -----------------------------------------------------------------------

        public static void AssignClipToState(AnimatorController controller, string layerName, string stateName, AnimationClip clip)
        {
            foreach (var layer in controller.layers)
            {
                if (layer.name != layerName) continue;
                foreach (var state in layer.stateMachine.states)
                {
                    if (state.state.name == stateName)
                    {
                        state.state.motion = clip;
                        EditorUtility.SetDirty(controller);
                        AssetDatabase.SaveAssets();
                        Debug.Log($"[Buddy] Assigned {clip.name} → {stateName}");
                        return;
                    }
                }
            }
            Debug.LogWarning($"[Buddy] State '{stateName}' not found in layer '{layerName}'");
        }

        private static void EnsureFolder(string path)
        {
            if (!AssetDatabase.IsValidFolder(path.TrimEnd('/')))
            {
                string parent = Path.GetDirectoryName(path.TrimEnd('/'));
                string folder = Path.GetFileName(path.TrimEnd('/'));
                AssetDatabase.CreateFolder(parent, folder);
            }
        }
    }
}
