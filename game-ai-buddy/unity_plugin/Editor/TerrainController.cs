using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

namespace GameAIBuddy
{
    /// <summary>
    /// AI-driven terrain controller.
    /// Can generate mountains, valleys, rivers, flatten areas, and apply texture layers.
    /// Called by the AI Buddy when it generates terrain-related C# code.
    /// </summary>
    public static class TerrainController
    {
        // ---------------------------------------------------------------
        //  Terrain creation
        // ---------------------------------------------------------------

        public static Terrain CreateTerrain(int width = 512, int height = 512, int resolution = 513)
        {
            TerrainData data = new TerrainData
            {
                heightmapResolution = resolution,
                size = new Vector3(width, 200, height),
            };

            GameObject terrainObj = Terrain.CreateTerrainGameObject(data);
            terrainObj.name = "AI_Terrain";
            Undo.RegisterCreatedObjectUndo(terrainObj, "Create AI Terrain");
            return terrainObj.GetComponent<Terrain>();
        }

        // ---------------------------------------------------------------
        //  Height operations
        // ---------------------------------------------------------------

        public static void RaiseMountain(Terrain terrain, Vector2 centerNorm, float radius, float height)
        {
            TerrainData data = terrain.terrainData;
            int res = data.heightmapResolution;
            float[,] heights = data.GetHeights(0, 0, res, res);

            int cx = Mathf.RoundToInt(centerNorm.x * (res - 1));
            int cy = Mathf.RoundToInt(centerNorm.y * (res - 1));
            int r = Mathf.RoundToInt(radius * res);

            for (int y = Mathf.Max(0, cy - r); y <= Mathf.Min(res - 1, cy + r); y++)
            {
                for (int x = Mathf.Max(0, cx - r); x <= Mathf.Min(res - 1, cx + r); x++)
                {
                    float dist = Vector2.Distance(new Vector2(x, y), new Vector2(cx, cy));
                    if (dist < r)
                    {
                        float influence = 1f - (dist / r);
                        influence = Mathf.SmoothStep(0, 1, influence);
                        heights[y, x] = Mathf.Clamp01(heights[y, x] + height * influence);
                    }
                }
            }

            data.SetHeights(0, 0, heights);
        }

        public static void Flatten(Terrain terrain, float targetHeight = 0f)
        {
            TerrainData data = terrain.terrainData;
            int res = data.heightmapResolution;
            float[,] heights = new float[res, res];

            for (int y = 0; y < res; y++)
                for (int x = 0; x < res; x++)
                    heights[y, x] = targetHeight;

            data.SetHeights(0, 0, heights);
        }

        public static void AddNoise(Terrain terrain, float scale = 50f, float strength = 0.05f)
        {
            TerrainData data = terrain.terrainData;
            int res = data.heightmapResolution;
            float[,] heights = data.GetHeights(0, 0, res, res);

            for (int y = 0; y < res; y++)
                for (int x = 0; x < res; x++)
                    heights[y, x] += Mathf.PerlinNoise(x / scale, y / scale) * strength;

            data.SetHeights(0, 0, heights);
        }

        public static void CarveRiver(Terrain terrain, List<Vector2> pathNorm, float width = 0.02f, float depth = 0.03f)
        {
            TerrainData data = terrain.terrainData;
            int res = data.heightmapResolution;
            float[,] heights = data.GetHeights(0, 0, res, res);

            for (int y = 0; y < res; y++)
            {
                for (int x = 0; x < res; x++)
                {
                    Vector2 p = new Vector2((float)x / res, (float)y / res);
                    float minDist = float.MaxValue;

                    for (int i = 0; i < pathNorm.Count - 1; i++)
                    {
                        float d = DistanceToSegment(p, pathNorm[i], pathNorm[i + 1]);
                        if (d < minDist) minDist = d;
                    }

                    if (minDist < width)
                    {
                        float influence = 1f - (minDist / width);
                        heights[y, x] = Mathf.Clamp01(heights[y, x] - depth * influence);
                    }
                }
            }

            data.SetHeights(0, 0, heights);
        }

        // ---------------------------------------------------------------
        //  Asset scatter / swap
        // ---------------------------------------------------------------

        public static void ScatterObjects(GameObject prefab, Terrain terrain, int count,
            float minSlope = 0f, float maxSlope = 30f, float yOffset = 0f)
        {
            if (prefab == null) { Debug.LogError("[Buddy] Prefab is null."); return; }

            TerrainData data = terrain.terrainData;
            int placed = 0;
            int attempts = 0;

            while (placed < count && attempts < count * 10)
            {
                attempts++;
                float nx = Random.value;
                float nz = Random.value;
                float slope = data.GetSteepness(nx, nz);

                if (slope < minSlope || slope > maxSlope) continue;

                Vector3 worldPos = terrain.transform.position + new Vector3(
                    nx * data.size.x,
                    0,
                    nz * data.size.z
                );
                worldPos.y = terrain.SampleHeight(worldPos) + yOffset;

                GameObject go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                go.transform.position = worldPos;
                go.transform.rotation = Quaternion.Euler(0, Random.Range(0f, 360f), 0);
                Undo.RegisterCreatedObjectUndo(go, "Buddy Scatter");
                placed++;
            }

            Debug.Log($"[Buddy] Placed {placed}/{count} {prefab.name} objects.");
        }

        public static void SwapAllOfType(GameObject oldPrefab, GameObject newPrefab)
        {
            GameObject[] all = GameObject.FindObjectsOfType<GameObject>();
            int swapped = 0;

            foreach (var go in all)
            {
                GameObject src = PrefabUtility.GetCorrespondingObjectFromSource(go);
                if (src == oldPrefab)
                {
                    Vector3 pos = go.transform.position;
                    Quaternion rot = go.transform.rotation;
                    Vector3 scale = go.transform.localScale;

                    Undo.DestroyObjectImmediate(go);

                    GameObject replacement = (GameObject)PrefabUtility.InstantiatePrefab(newPrefab);
                    replacement.transform.SetPositionAndRotation(pos, rot);
                    replacement.transform.localScale = scale;
                    Undo.RegisterCreatedObjectUndo(replacement, "Buddy Swap");
                    swapped++;
                }
            }

            Debug.Log($"[Buddy] Swapped {swapped} objects from {oldPrefab.name} to {newPrefab.name}.");
        }

        // ---------------------------------------------------------------
        //  Helpers
        // ---------------------------------------------------------------

        private static float DistanceToSegment(Vector2 p, Vector2 a, Vector2 b)
        {
            Vector2 ab = b - a;
            float t = Mathf.Clamp01(Vector2.Dot(p - a, ab) / ab.sqrMagnitude);
            return Vector2.Distance(p, a + t * ab);
        }
    }
}
