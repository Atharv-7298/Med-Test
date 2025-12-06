const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const connectDB = require("./config/db");
const pipelineRoutes = require("./routes/pipelineRoutes");

dotenv.config();
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Connect DB
connectDB();

// Routes
app.use("/api/ehr", require("./routes/ehrRoutes"));   // your existing EHR routes
app.use("/api/auth", require("./routes/authRoutes")); // new auth routes
app.use("/api/pipeline", require("./routes/pipelineRoutes"));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
