using UnityEngine;
using UnityEditor;

namespace GameAIBuddy
{
    /// <summary>
    /// Creates fully configured Particle Systems in code — no assets needed.
    /// Call from AI-generated code or the Mechanics window directly.
    /// All methods return the created GameObject so you can position/parent it.
    /// </summary>
    public static class ParticlePresets
    {
        // -----------------------------------------------------------------------
        //  Fire
        // -----------------------------------------------------------------------

        public static GameObject CreateFire(string name = "FireEffect", Transform parent = null)
        {
            var root = new GameObject(name);
            if (parent) root.transform.SetParent(parent, false);
            Undo.RegisterCreatedObjectUndo(root, "Create Fire Effect");

            // Core flames
            var ps = root.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.8f, 1.5f);
            main.startSpeed    = new ParticleSystem.MinMaxCurve(0.5f, 2.0f);
            main.startSize     = new ParticleSystem.MinMaxCurve(0.3f, 1.2f);
            main.startRotation = new ParticleSystem.MinMaxCurve(0f, 360f);
            main.gravityModifier = -0.1f;
            main.maxParticles = 200;

            // Orange → yellow → transparent
            var col = ps.colorOverLifetime;
            col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(
                new[] { new GradientColorKey(new Color(1f, 0.3f, 0f), 0f),
                         new GradientColorKey(new Color(1f, 0.8f, 0f), 0.4f),
                         new GradientColorKey(new Color(1f, 1f, 0.5f), 1f) },
                new[] { new GradientAlphaKey(0f, 0f),
                         new GradientAlphaKey(1f, 0.1f),
                         new GradientAlphaKey(0.8f, 0.5f),
                         new GradientAlphaKey(0f, 1f) }
            );
            col.color = new ParticleSystem.MinMaxGradient(grad);

            // Cone emission upward
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = 15f;
            shape.radius = 0.3f;

            var emission = ps.emission;
            emission.rateOverTime = 40f;

            // Size over lifetime (grow then shrink)
            var sizeOL = ps.sizeOverLifetime;
            sizeOL.enabled = true;
            var sizeCurve = new AnimationCurve(
                new Keyframe(0f, 0f), new Keyframe(0.2f, 1f), new Keyframe(1f, 0.3f));
            sizeOL.size = new ParticleSystem.MinMaxCurve(1f, sizeCurve);

            // Renderer — Additive for glow
            var renderer = root.GetComponent<ParticleSystemRenderer>();
            renderer.renderMode = ParticleSystemRenderMode.Billboard;
            renderer.sortingFudge = -1f;
            renderer.material = CreateAdditiveMaterial(new Color(1f, 0.5f, 0f));

            // Sparks sub-system
            var sparksObj = new GameObject("Sparks");
            sparksObj.transform.SetParent(root.transform, false);
            var sparks = sparksObj.AddComponent<ParticleSystem>();
            var sm = sparks.main;
            sm.startLifetime = new ParticleSystem.MinMaxCurve(0.5f, 1.5f);
            sm.startSpeed    = new ParticleSystem.MinMaxCurve(1f, 4f);
            sm.startSize     = new ParticleSystem.MinMaxCurve(0.02f, 0.06f);
            sm.gravityModifier = 0.3f;
            sm.maxParticles  = 80;
            var se = sparks.emission;
            se.rateOverTime = 15f;
            var sparkRenderer = sparksObj.GetComponent<ParticleSystemRenderer>();
            sparkRenderer.material = CreateAdditiveMaterial(new Color(1f, 0.9f, 0.2f));

            // Flickering light
            var lightObj = new GameObject("FireLight");
            lightObj.transform.SetParent(root.transform, false);
            lightObj.transform.localPosition = Vector3.up * 0.5f;
            var light = lightObj.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = new Color(1f, 0.5f, 0.1f);
            light.intensity = 2f;
            light.range = 4f;
            lightObj.AddComponent<FireLightFlicker>();

            Debug.Log($"[Buddy] Created fire effect: {name}");
            return root;
        }

        // -----------------------------------------------------------------------
        //  Explosion
        // -----------------------------------------------------------------------

        public static GameObject CreateExplosion(Vector3 worldPosition, float scale = 1f)
        {
            var root = new GameObject("Explosion");
            root.transform.position = worldPosition;
            Undo.RegisterCreatedObjectUndo(root, "Create Explosion");

            // Flash
            AddExplosionLayer(root, "Flash",
                burstCount: 60, lifetime: new Vector2(0.1f, 0.25f),
                speed: new Vector2(2f, 8f) * scale, size: new Vector2(0.3f, 0.8f) * scale,
                colorStart: Color.white, colorEnd: new Color(1f, 0.6f, 0f),
                gravity: 0f, additive: true);

            // Debris
            AddExplosionLayer(root, "Debris",
                burstCount: 40, lifetime: new Vector2(0.8f, 2f),
                speed: new Vector2(3f, 12f) * scale, size: new Vector2(0.05f, 0.2f) * scale,
                colorStart: new Color(0.4f, 0.2f, 0.1f), colorEnd: new Color(0.1f, 0.1f, 0.1f),
                gravity: 1.2f, additive: false);

            // Smoke
            AddExplosionSmoke(root, scale);

            // Light burst
            var lightObj = new GameObject("ExplosionLight");
            lightObj.transform.SetParent(root.transform, false);
            var lt = lightObj.AddComponent<Light>();
            lt.type = LightType.Point;
            lt.color = new Color(1f, 0.6f, 0.2f);
            lt.intensity = 8f * scale;
            lt.range = 12f * scale;
            lightObj.AddComponent<FadeLight>();

            Debug.Log($"[Buddy] Created explosion at {worldPosition}");
            return root;
        }

        private static void AddExplosionLayer(GameObject parent, string layerName,
            int burstCount, Vector2 lifetime, Vector2 speed, Vector2 size,
            Color colorStart, Color colorEnd, float gravity, bool additive)
        {
            var obj = new GameObject(layerName);
            obj.transform.SetParent(parent.transform, false);
            var ps = obj.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = false;
            main.startLifetime = new ParticleSystem.MinMaxCurve(lifetime.x, lifetime.y);
            main.startSpeed    = new ParticleSystem.MinMaxCurve(speed.x,    speed.y);
            main.startSize     = new ParticleSystem.MinMaxCurve(size.x,     size.y);
            main.gravityModifier = gravity;
            main.startColor    = new ParticleSystem.MinMaxGradient(colorStart, colorEnd);

            var emission = ps.emission;
            emission.SetBursts(new[] { new ParticleSystem.Burst(0f, burstCount) });
            emission.rateOverTime = 0;

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Sphere;
            shape.radius = 0.1f;

            var renderer = obj.GetComponent<ParticleSystemRenderer>();
            renderer.material = additive
                ? CreateAdditiveMaterial(Color.white)
                : CreateDefaultMaterial(Color.grey);
        }

        private static void AddExplosionSmoke(GameObject parent, float scale)
        {
            var obj = new GameObject("Smoke");
            obj.transform.SetParent(parent.transform, false);
            var ps = obj.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = false;
            main.duration = 2f;
            main.startDelay = 0.1f;
            main.startLifetime = new ParticleSystem.MinMaxCurve(2f, 4f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(0.5f, 2f * scale);
            main.startSize  = new ParticleSystem.MinMaxCurve(1f * scale, 3f * scale);
            main.gravityModifier = -0.05f;

            var col = ps.colorOverLifetime;
            col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(
                new[] { new GradientColorKey(new Color(0.3f, 0.3f, 0.3f), 0f),
                         new GradientColorKey(new Color(0.5f, 0.5f, 0.5f), 1f) },
                new[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(0.6f, 0.2f), new GradientAlphaKey(0f, 1f) }
            );
            col.color = new ParticleSystem.MinMaxGradient(grad);

            var emission = ps.emission;
            emission.rateOverTime = 8;
            emission.SetBursts(new[] { new ParticleSystem.Burst(0f, 20) });
        }

        // -----------------------------------------------------------------------
        //  Magic aura
        // -----------------------------------------------------------------------

        public static GameObject CreateMagicAura(Color color, Transform parent = null, string name = "MagicAura")
        {
            var root = new GameObject(name);
            if (parent) root.transform.SetParent(parent, false);
            Undo.RegisterCreatedObjectUndo(root, "Create Magic Aura");

            // Orbiting particles
            var orbObj = new GameObject("Orbit");
            orbObj.transform.SetParent(root.transform, false);
            var orbit = orbObj.AddComponent<ParticleSystem>();
            var om = orbit.main;
            om.startLifetime = new ParticleSystem.MinMaxCurve(2f, 3f);
            om.startSpeed = 0.5f;
            om.startSize = new ParticleSystem.MinMaxCurve(0.05f, 0.15f);
            var oshape = orbit.shape;
            oshape.shapeType = ParticleSystemShapeType.Circle;
            oshape.radius = 0.8f;
            var oe = orbit.emission;
            oe.rateOverTime = 20f;
            var ovel = orbit.velocityOverLifetime;
            ovel.enabled = true;
            ovel.orbitalY = 2f;
            var orend = orbObj.GetComponent<ParticleSystemRenderer>();
            orend.material = CreateAdditiveMaterial(color);

            // Rising sparkles
            var sparkObj = new GameObject("Sparkles");
            sparkObj.transform.SetParent(root.transform, false);
            var spark = sparkObj.AddComponent<ParticleSystem>();
            var sm = spark.main;
            sm.startLifetime = new ParticleSystem.MinMaxCurve(0.8f, 1.5f);
            sm.startSpeed = new ParticleSystem.MinMaxCurve(0.3f, 1f);
            sm.startSize = new ParticleSystem.MinMaxCurve(0.02f, 0.08f);
            sm.gravityModifier = -0.3f;
            var sshape = spark.shape;
            sshape.shapeType = ParticleSystemShapeType.Cylinder;
            sshape.radius = 0.4f;
            sshape.length = 1f;
            var se = spark.emission;
            se.rateOverTime = 15f;
            var srend = sparkObj.GetComponent<ParticleSystemRenderer>();
            srend.material = CreateAdditiveMaterial(Color.white);

            // Glow light
            var lightObj = new GameObject("AuraLight");
            lightObj.transform.SetParent(root.transform, false);
            var lt = lightObj.AddComponent<Light>();
            lt.type = LightType.Point;
            lt.color = color;
            lt.intensity = 1f;
            lt.range = 3f;
            lightObj.AddComponent<PulseLight>();

            Debug.Log($"[Buddy] Created magic aura: {name}");
            return root;
        }

        // -----------------------------------------------------------------------
        //  Weather — Rain
        // -----------------------------------------------------------------------

        public static GameObject CreateRain(float intensity = 1f, string name = "RainSystem")
        {
            var root = new GameObject(name);
            Undo.RegisterCreatedObjectUndo(root, "Create Rain");

            var ps = root.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.4f, 0.8f);
            main.startSpeed    = new ParticleSystem.MinMaxCurve(8f, 12f);
            main.startSize     = new ParticleSystem.MinMaxCurve(0.02f, 0.06f);
            main.startRotation = 15f * Mathf.Deg2Rad;
            main.gravityModifier = 1f;
            main.maxParticles  = (int)(3000 * intensity);

            var em = ps.emission;
            em.rateOverTime = 800f * intensity;

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(30f, 1f, 30f);
            shape.position = new Vector3(0f, 10f, 0f);

            var renderer = root.GetComponent<ParticleSystemRenderer>();
            renderer.renderMode = ParticleSystemRenderMode.Stretch;
            renderer.lengthScale = 3f;
            renderer.material = CreateAdditiveMaterial(new Color(0.7f, 0.8f, 1f, 0.6f));

            Debug.Log($"[Buddy] Created rain system (intensity {intensity})");
            return root;
        }

        // -----------------------------------------------------------------------
        //  Footstep dust
        // -----------------------------------------------------------------------

        public static GameObject CreateFootstepDust(string name = "FootstepDust")
        {
            var root = new GameObject(name);
            Undo.RegisterCreatedObjectUndo(root, "Create Footstep Dust");

            var ps = root.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = false;
            main.duration = 0.3f;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.3f, 0.6f);
            main.startSpeed    = new ParticleSystem.MinMaxCurve(0.5f, 1.5f);
            main.startSize     = new ParticleSystem.MinMaxCurve(0.1f, 0.3f);
            main.startColor    = new Color(0.8f, 0.7f, 0.5f, 0.6f);
            main.gravityModifier = 0.1f;

            var em = ps.emission;
            em.SetBursts(new[] { new ParticleSystem.Burst(0f, 8) });
            em.rateOverTime = 0f;

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.1f;
            shape.rotation = new Vector3(-90f, 0f, 0f);

            var col = ps.colorOverLifetime;
            col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(
                new[] { new GradientColorKey(new Color(0.8f, 0.7f, 0.5f), 0f), new GradientColorKey(Color.grey, 1f) },
                new[] { new GradientAlphaKey(0.8f, 0f), new GradientAlphaKey(0f, 1f) }
            );
            col.color = new ParticleSystem.MinMaxGradient(grad);

            Debug.Log($"[Buddy] Created footstep dust prefab: {name}");
            return root;
        }

        // -----------------------------------------------------------------------
        //  Level-up sparkle
        // -----------------------------------------------------------------------

        public static GameObject CreateLevelUpEffect(Transform parent = null)
        {
            var root = new GameObject("LevelUpEffect");
            if (parent) root.transform.SetParent(parent, false);
            Undo.RegisterCreatedObjectUndo(root, "Create Level Up Effect");

            // Stars burst
            var starsObj = new GameObject("Stars");
            starsObj.transform.SetParent(root.transform, false);
            var stars = starsObj.AddComponent<ParticleSystem>();
            var sm = stars.main;
            sm.loop = false;
            sm.startLifetime = new ParticleSystem.MinMaxCurve(0.8f, 1.4f);
            sm.startSpeed    = new ParticleSystem.MinMaxCurve(2f, 5f);
            sm.startSize     = new ParticleSystem.MinMaxCurve(0.1f, 0.3f);
            sm.startColor    = new ParticleSystem.MinMaxGradient(Color.yellow, Color.white);
            sm.gravityModifier = -0.2f;
            var se = stars.emission;
            se.SetBursts(new[] { new ParticleSystem.Burst(0f, 30) });
            se.rateOverTime = 0;
            var ss = stars.shape;
            ss.shapeType = ParticleSystemShapeType.Sphere;
            ss.radius = 0.1f;
            var srend = starsObj.GetComponent<ParticleSystemRenderer>();
            srend.material = CreateAdditiveMaterial(Color.yellow);

            // Rising column
            var colObj = new GameObject("Column");
            colObj.transform.SetParent(root.transform, false);
            var col = colObj.AddComponent<ParticleSystem>();
            var cm = col.main;
            cm.loop = false;
            cm.duration = 1.5f;
            cm.startLifetime = new ParticleSystem.MinMaxCurve(0.5f, 1f);
            cm.startSpeed    = new ParticleSystem.MinMaxCurve(3f, 6f);
            cm.startSize     = new ParticleSystem.MinMaxCurve(0.2f, 0.5f);
            cm.gravityModifier = -0.8f;
            var ce = col.emission;
            ce.rateOverTime = 30f;
            var cs = col.shape;
            cs.shapeType = ParticleSystemShapeType.Circle;
            cs.radius = 0.5f;
            cs.rotation = new Vector3(-90f, 0, 0);
            var crend = colObj.GetComponent<ParticleSystemRenderer>();
            crend.material = CreateAdditiveMaterial(new Color(0.5f, 0.8f, 1f));

            Debug.Log("[Buddy] Created level-up effect.");
            return root;
        }

        // -----------------------------------------------------------------------
        //  Material helpers (no assets needed)
        // -----------------------------------------------------------------------

        private static Material CreateAdditiveMaterial(Color color)
        {
            var mat = new Material(Shader.Find("Particles/Standard Unlit") ?? Shader.Find("Legacy Shaders/Particles/Additive"));
            if (mat.shader == null) mat.shader = Shader.Find("Universal Render Pipeline/Particles/Unlit");
            mat.SetColor("_Color", color);
            mat.SetFloat("_Mode", 1f);
            mat.EnableKeyword("_ALPHAPREMULTIPLY_ON");
            mat.renderQueue = 3000;
            return mat;
        }

        private static Material CreateDefaultMaterial(Color color)
        {
            var mat = new Material(Shader.Find("Universal Render Pipeline/Particles/Lit") ?? Shader.Find("Standard"));
            mat.color = color;
            return mat;
        }
    }

    // -----------------------------------------------------------------------
    //  Small helper MonoBehaviours (dropped onto particle light GameObjects)
    // -----------------------------------------------------------------------

    public class FireLightFlicker : MonoBehaviour
    {
        private Light _light;
        private float _baseIntensity;
        void Start() { _light = GetComponent<Light>(); _baseIntensity = _light.intensity; }
        void Update()
        {
            _light.intensity = _baseIntensity + Mathf.PerlinNoise(Time.time * 8f, 0f) * 1.5f
                             - Mathf.PerlinNoise(Time.time * 3f, 1f) * 0.5f;
        }
    }

    public class FadeLight : MonoBehaviour
    {
        private Light _light;
        private float _startIntensity;
        private float _elapsed;
        [SerializeField] private float duration = 0.4f;
        void Start() { _light = GetComponent<Light>(); _startIntensity = _light.intensity; }
        void Update()
        {
            _elapsed += Time.deltaTime;
            _light.intensity = Mathf.Lerp(_startIntensity, 0f, _elapsed / duration);
            if (_elapsed >= duration) Destroy(gameObject);
        }
    }

    public class PulseLight : MonoBehaviour
    {
        private Light _light;
        private float _base;
        [SerializeField] private float pulseSpeed = 2f;
        [SerializeField] private float pulseAmount = 0.4f;
        void Start() { _light = GetComponent<Light>(); _base = _light.intensity; }
        void Update() { _light.intensity = _base + Mathf.Sin(Time.time * pulseSpeed) * pulseAmount; }
    }
}
