import React, { useState } from "react";
import { FaPlay, FaStop } from "react-icons/fa";
import "./Consultation.css";
import api from "../../../services/api";

export default function ConsultationCard() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [summary, setSummary] = useState("");
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");

  const startRecording = async () => {
    setSummary("");
    setTranscript("");
    setError("");

    try {
      await api.post("/pipeline/start");
      setIsRecording(true);
    } catch (err) {
      console.error(err);
      setError("Failed to start recording.");
    }
  };

  const stopRecording = async () => {
    setIsRecording(false);
    setIsProcessing(true);

    try {
      const res = await api.post("/pipeline/stop");

      if (res.data.error) {
        setError(res.data.error);
      } else {
        setTranscript(res.data.transcript);
        setSummary(res.data.summary);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to stop pipeline.");
    }

    setIsProcessing(false);
  };

  return (
    <div className="consult-card">
      <div className="consult-header">
        <h3>AI-Powered Consultation</h3>
        <p>Record conversation → Stop → Get Transcript + Summary</p>
      </div>

      <div className="consult-body">

        {/* Start button */}
        {!isRecording && !isProcessing && !summary && (
          <button className="primary-btn" onClick={startRecording}>
            <FaPlay /> Start Conversation
          </button>
        )}

        {/* Recording UI */}
        {isRecording && (
          <div className="recording-layout">
            <div className="recording-status-center">
              <span className="pulse-dot" /> Listening...
            </div>

            <button className="stop-btn" onClick={stopRecording}>
              <FaStop /> Stop
            </button>

            <p className="recording-hint">AI is listening 👂 Speak naturally.</p>
          </div>
        )}

        {/* Processing UI */}
        {isProcessing && (
          <div className="processing-box">
            <div className="loader"></div>
            <p>Processing… generating transcript & summary</p>
          </div>
        )}

        {/* Show Results */}
        {summary && !isRecording && (
          <div className="result-box">
            <h3>Clinical Summary</h3>
            <p>{summary}</p>

            <h3 style={{ marginTop: "20px" }}>Full Transcript</h3>
            <p className="transcript-box">{transcript}</p>
          </div>
        )}

        {/* Error */}
        {error && <p className="error-text">{error}</p>}
      </div>
    </div>
  );
}
