using System;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

namespace GameAIBuddy
{
    /// <summary>
    /// HTTP client that talks to the local Game AI Buddy server.
    /// </summary>
    public static class BuddyClient
    {
        public const string ServerUrl = "http://127.0.0.1:8765";

        [Serializable]
        private class AskRequest
        {
            public string prompt;
            public string app = "unity";
            public bool include_screenshot = false;
        }

        [Serializable]
        public class AskResponse
        {
            public string reply;
            public string provider;
            public bool had_screenshot;
        }

        [Serializable]
        private class StatusResponse
        {
            public bool online;
            public string provider;
            public bool gemini_configured;
            public string model;
        }

        public static async Task<AskResponse> Ask(string prompt, bool includeScreenshot = false)
        {
            var requestBody = new AskRequest
            {
                prompt = prompt,
                app = "unity",
                include_screenshot = includeScreenshot,
            };

            string json = JsonUtility.ToJson(requestBody);
            byte[] body = Encoding.UTF8.GetBytes(json);

            using var req = new UnityWebRequest($"{ServerUrl}/ask", "POST");
            req.uploadHandler = new UploadHandlerRaw(body);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");

            var op = req.SendWebRequest();
            while (!op.isDone)
                await Task.Yield();

            if (req.result != UnityWebRequest.Result.Success)
                throw new Exception($"Buddy server error: {req.error}\nMake sure the server is running: python server/main.py");

            return JsonUtility.FromJson<AskResponse>(req.downloadHandler.text);
        }

        public static async Task<bool> CheckOnline()
        {
            try
            {
                using var req = UnityWebRequest.Get($"{ServerUrl}/status");
                req.timeout = 3;
                var op = req.SendWebRequest();
                while (!op.isDone)
                    await Task.Yield();
                return req.result == UnityWebRequest.Result.Success;
            }
            catch { return false; }
        }
    }
}
