using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;

namespace GameAIBuddy
{
    /// <summary>
    /// Unity Procedural Content Generation controller.
    /// Handles terrain painting, foliage scattering, biome population,
    /// and asset management — all callable from AI-generated C# code.
    /// </summary>
    public static class PCGController
    {
        // -----------------------------------------------------------------------
        //  Biome definitions
        // -----------------------------------------------------------------------

        public class BiomeLayer
        {
            public string Name;
            public string[] PrefabPaths;   // paths relative to Assets/ or Resources/
            public int Count;
            public float SlopeMin, SlopeMax;
            public float AltitudeMin, AltitudeMax;
            public float ScaleMin, ScaleMax;
            public string TagName;
        }

        public class BiomeConfig
        {
            public string Label;
            public BiomeLayer[] Layers;
        }

        public static readonly Dictionary<string, BiomeConfig> Biomes = new Dictionary<string, BiomeConfig>
        {
            ["forest"] = new BiomeConfig
            {
                Label = "Temperate Forest",
                Layers = new[]
                {
                    new BiomeLayer { Name = "Trees",      Count = 300, SlopeMin = 0, SlopeMax = 25, AltitudeMin = 0,    AltitudeMax = 200,  ScaleMin = 0.8f, ScaleMax = 1.4f, TagName = "BuddyTree"  },
                    new BiomeLayer { Name = "Undergrowth", Count = 600, SlopeMin = 0, SlopeMax = 30, AltitudeMin = 0,    AltitudeMax = 150,  ScaleMin = 0.4f, ScaleMax = 0.9f, TagName = "BuddyGround" },
                    new BiomeLayer { Name = "Rocks",       Count = 120, SlopeMin = 5, SlopeMax = 45, AltitudeMin = 0,    AltitudeMax = 300,  ScaleMin = 0.5f, ScaleMax = 2.0f, TagName = "BuddyRock"  },
                }
            },
            ["desert"] = new BiomeConfig
            {
                Label = "Desert / Arid",
                Layers = new[]
                {
                    new BiomeLayer { Name = "Cacti",    Count = 150, SlopeMin = 0, SlopeMax = 20, AltitudeMin = 0, AltitudeMax = 100, ScaleMin = 0.7f, ScaleMax = 1.5f, TagName = "BuddyVeg"  },
                    new BiomeLayer { Name = "Rocks",    Count = 300, SlopeMin = 0, SlopeMax = 50, AltitudeMin = 0, AltitudeMax = 200, ScaleMin = 0.5f, ScaleMax = 3.0f, TagName = "BuddyRock" },
                    new BiomeLayer { Name = "Shrubs",   Count = 400, SlopeMin = 0, SlopeMax = 35, AltitudeMin = 0, AltitudeMax = 150, ScaleMin = 0.4f, ScaleMax = 0.9f, TagName = "BuddyGround"},
                }
            },
            ["mountain"] = new BiomeConfig
            {
                Label = "Alpine Mountain",
                Layers = new[]
                {
                    new BiomeLayer { Name = "Pine Trees", Count = 250, SlopeMin = 0,  SlopeMax = 35, AltitudeMin = 50,  AltitudeMax = 300, ScaleMin = 0.9f, ScaleMax = 1.6f, TagName = "BuddyTree" },
                    new BiomeLayer { Name = "Boulders",   Count = 350, SlopeMin = 15, SlopeMax = 70, AltitudeMin = 80,  AltitudeMax = 500, ScaleMin = 0.8f, ScaleMax = 4.0f, TagName = "BuddyRock" },
                }
            },
            ["swamp"] = new BiomeConfig
            {
                Label = "Swamp / Wetland",
                Layers = new[]
                {
                    new BiomeLayer { Name = "Dead Trees", Count = 200, SlopeMin = 0, SlopeMax = 15, AltitudeMin = -5,  AltitudeMax = 30,  ScaleMin = 0.7f, ScaleMax = 1.6f, TagName = "BuddyTree"  },
                    new BiomeLayer { Name = "Tall Grass", Count = 800, SlopeMin = 0, SlopeMax = 10, AltitudeMin = -10, AltitudeMax = 20,  ScaleMin = 0.5f, ScaleMax = 1.2f, TagName = "BuddyGround" },
                    new BiomeLayer { Name = "Mossy Rock", Count = 150, SlopeMin = 0, SlopeMax = 30, AltitudeMin = -10, AltitudeMax = 40,  ScaleMin = 0.5f, ScaleMax = 2.5f, TagName = "BuddyRock"  },
                }
            },
            ["coastal"] = new BiomeConfig
            {
                Label = "Coastal / Beach",
                Layers = new[]
                {
                    new BiomeLayer { Name = "Palm Trees",   Count = 80,  SlopeMin = 0, SlopeMax = 20, AltitudeMin = 0, AltitudeMax = 30,  ScaleMin = 0.8f, ScaleMax = 1.3f, TagName = "BuddyTree" },
                    new BiomeLayer { Name = "Coastal Rock", Count = 180, SlopeMin = 0, SlopeMax = 40, AltitudeMin = 0, AltitudeMax = 50,  ScaleMin = 0.5f, ScaleMax = 2.0f, TagName = "BuddyRock" },
                }
            },
        };

        // -----------------------------------------------------------------------
        //  Biome population
        // -----------------------------------------------------------------------

        /// <summary>
        /// Populate terrain with the named biome.
        /// prefabMap: map from layer names to actual prefab arrays (loaded by caller or AI code).
        /// </summary>
        public static int PopulateBiome(
            string biomeName,
            Terrain terrain,
            Dictionary<string, GameObject[]> prefabMap,
            float densityMultiplier = 1f,
            bool clearExisting = true)
        {
            if (!Biomes.TryGetValue(biomeName.ToLower(), out var config))
            {
                Debug.LogError($"[Buddy PCG] Unknown biome '{biomeName}'. Valid: {string.Join(", ", Biomes.Keys)}");
                return 0;
            }

            if (clearExisting)
                ClearBuddyActors();

            int total = 0;
            foreach (var layer in config.Layers)
            {
                if (!prefabMap.TryGetValue(layer.Name, out var prefabs) || prefabs == null || prefabs.Length == 0)
                {
                    Debug.LogWarning($"[Buddy PCG] No prefabs for layer '{layer.Name}' in biome '{biomeName}' — skipping.");
                    continue;
                }

                int count = Mathf.RoundToInt(layer.Count * densityMultiplier);
                int placed = ScatterLayer(terrain, prefabs, count, layer);
                total += placed;
                Debug.Log($"[Buddy PCG]   {layer.Name}: {placed} placed");
            }

            Debug.Log($"[Buddy PCG] Biome '{config.Label}' complete. Total: {total} objects.");
            return total;
        }

        private static int ScatterLayer(Terrain terrain, GameObject[] prefabs, int count, BiomeLayer layer)
        {
            var data = terrain.terrainData;
            int placed = 0;

            Undo.RegisterCompleteObjectUndo(terrain, $"Buddy Scatter {layer.Name}");

            for (int attempt = 0; attempt < count * 8 && placed < count; attempt++)
            {
                float nx = Random.value;
                float nz = Random.value;
                float slope = data.GetSteepness(nx, nz);

                if (slope < layer.SlopeMin || slope > layer.SlopeMax) continue;

                Vector3 worldPos = new Vector3(
                    terrain.transform.position.x + nx * data.size.x,
                    0,
                    terrain.transform.position.z + nz * data.size.z
                );
                worldPos.y = terrain.SampleHeight(worldPos);

                if (worldPos.y < layer.AltitudeMin || worldPos.y > layer.AltitudeMax) continue;

                var prefab = prefabs[Random.Range(0, prefabs.Length)];
                float scale = Random.Range(layer.ScaleMin, layer.ScaleMax);

                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                go.transform.position = worldPos;
                go.transform.rotation = Quaternion.Euler(0, Random.Range(0f, 360f), 0);
                go.transform.localScale = Vector3.one * scale;
                go.tag = layer.TagName;
                Undo.RegisterCreatedObjectUndo(go, $"Buddy PCG {layer.Name}");
                placed++;
            }

            return placed;
        }

        // -----------------------------------------------------------------------
        //  Terrain painting
        // -----------------------------------------------------------------------

        /// <summary>
        /// Paint terrain texture layers based on slope and altitude.
        /// Layers should be: [0]=flat ground, [1]=slope, [2]=high altitude, [3]=steep cliff
        /// </summary>
        public static void PaintByRules(Terrain terrain)
        {
            var data = terrain.terrainData;
            int w = data.alphamapWidth;
            int h = data.alphamapHeight;
            int layers = data.alphamapLayers;

            if (layers < 2)
            {
                Debug.LogWarning("[Buddy PCG] Terrain needs at least 2 texture layers for painting.");
                return;
            }

            float[,,] maps = new float[h, w, layers];

            for (int y = 0; y < h; y++)
            {
                for (int x = 0; x < w; x++)
                {
                    float nx = (float)x / w;
                    float nz = (float)y / h;
                    float slope = data.GetSteepness(nx, nz) / 90f;
                    float altitude = terrain.SampleHeight(new Vector3(nx * data.size.x, 0, nz * data.size.z)) / data.size.y;

                    float[] weights = new float[layers];

                    // Layer 0: flat ground
                    weights[0] = Mathf.Clamp01(1f - slope * 3f) * Mathf.Clamp01(1f - altitude * 2f);

                    // Layer 1: slope / rock (if exists)
                    if (layers > 1)
                        weights[1] = Mathf.Clamp01(slope * 2f);

                    // Layer 2: high altitude / snow (if exists)
                    if (layers > 2)
                        weights[2] = Mathf.Clamp01((altitude - 0.5f) * 3f) * (1f - slope);

                    // Layer 3: cliff (if exists)
                    if (layers > 3)
                        weights[3] = Mathf.Clamp01((slope - 0.6f) * 5f);

                    // Normalise
                    float total = weights.Sum();
                    if (total > 0)
                        for (int l = 0; l < layers; l++)
                            maps[y, x, l] = weights[l] / total;
                }
            }

            data.SetAlphamaps(0, 0, maps);
            Debug.Log("[Buddy PCG] Terrain painted by slope/altitude rules.");
        }

        // -----------------------------------------------------------------------
        //  Asset management
        // -----------------------------------------------------------------------

        /// <summary>Remove all GameObjects tagged with a Buddy tag.</summary>
        public static void ClearBuddyActors(string tagPrefix = "Buddy")
        {
            var buddyTags = new[] { "BuddyTree", "BuddyRock", "BuddyGround", "BuddyVeg", "BuddyBiome" };
            int removed = 0;
            foreach (var tag in buddyTags)
            {
                try
                {
                    var objects = GameObject.FindGameObjectsWithTag(tag);
                    foreach (var go in objects)
                    {
                        Undo.DestroyObjectImmediate(go);
                        removed++;
                    }
                }
                catch { }
            }
            Debug.Log($"[Buddy PCG] Cleared {removed} buddy actors.");
        }

        /// <summary>
        /// Swap all instances of oldPrefab with newPrefab. Preserves transforms.
        /// </summary>
        public static int SwapPrefabs(GameObject oldPrefab, GameObject newPrefab)
        {
            int swapped = 0;
            var all = Object.FindObjectsOfType<GameObject>();
            var toSwap = all.Where(go => PrefabUtility.GetCorrespondingObjectFromSource(go) == oldPrefab).ToList();

            foreach (var go in toSwap)
            {
                var pos = go.transform.position;
                var rot = go.transform.rotation;
                var scl = go.transform.localScale;
                Undo.DestroyObjectImmediate(go);
                var replacement = (GameObject)PrefabUtility.InstantiatePrefab(newPrefab);
                replacement.transform.SetPositionAndRotation(pos, rot);
                replacement.transform.localScale = scl;
                Undo.RegisterCreatedObjectUndo(replacement, "Buddy Swap");
                swapped++;
            }

            Debug.Log($"[Buddy PCG] Swapped {swapped} {oldPrefab.name} → {newPrefab.name}");
            return swapped;
        }

        /// <summary>Get a summary of all buddy-placed objects in the scene.</summary>
        public static string GetSceneSummary()
        {
            var buddyTags = new[] { "BuddyTree", "BuddyRock", "BuddyGround", "BuddyVeg" };
            var lines = new List<string> { "=== Buddy Scene Summary ===" };
            foreach (var tag in buddyTags)
            {
                try { lines.Add($"  {tag}: {GameObject.FindGameObjectsWithTag(tag).Length}"); }
                catch { }
            }
            var summary = string.Join("\n", lines);
            Debug.Log(summary);
            return summary;
        }
    }
}
