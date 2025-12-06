const express = require("express");
const { startConversation, stopConversation } = require("../controllers/pipelineController");
const router = express.Router();

router.post("/start", startConversation);
router.post("/stop", stopConversation);

module.exports = router;
