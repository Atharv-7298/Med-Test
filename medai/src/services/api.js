// medai/src/services/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api",
});

export const startConversationPipeline = async () => {
  const res = await api.post("/pipeline/start");
  return res.data; // { transcript, summary, ... }
};

export default api;
