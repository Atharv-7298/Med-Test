const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
let { pythonProcess } = require("../pipelineProcess");

// Start Recording
exports.startConversation = (req, res) => {
  if (pythonProcess) {
    return res.status(400).json({ error: "Recording already running" });
  }

  const scriptPath = path.join(__dirname, "..", "ai", "asr_realtime.py");

  pythonProcess = spawn("python", [scriptPath], {
    stdio: ["pipe", "pipe", "pipe"]
  });

  console.log("🎤 Python recording started...");

  return res.json({ status: "recording_started" });
};

// STOP Recording → Kill python → Read Transcript → Summarize
exports.stopConversation = (req, res) => {
  if (!pythonProcess) {
    return res.status(400).json({ error: "No active recording" });
  }

  console.log("🛑 Stopping recording...");

  pythonProcess.kill("SIGINT"); // stop python

  let output = "";
  let errorOutput = "";

  pythonProcess.stdout.on("data", (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on("data", (data) => {
    errorOutput += data.toString();
  });

  pythonProcess.on("close", () => {
    pythonProcess = null;

    try {
      const data = JSON.parse(output);
      return res.json(data);
    } catch (e) {
      return res.status(500).json({
        error: "Failed to parse pipeline output",
        output,
        errorOutput
      });
    }
  });
};
