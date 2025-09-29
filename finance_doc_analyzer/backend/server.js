import express from "express";
import multer from "multer";
import cors from "cors";
import axios from "axios";
import FormData from "form-data";
import { v4 as uuidv4 } from "uuid";
import { FileModel } from "./mongodb.js"; // import MongoDB connection + model

const app = express();
const PORT = process.env.PORT || 5050;
const token = "devtoken123";

app.use(cors());
app.use(express.json());
const upload = multer();

// Auth middleware
const authMiddleware = (req, res, next) => {
  const auth = req.headers.authorization;
  if (!auth || auth !== `Bearer ${token}`)
    return res.status(401).json({ error: "Unauthorized" });
  next();
};

// Upload
app.post("/api/upload/analyze", authMiddleware, upload.single("file"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file uploaded" });
  const fileId = uuidv4();
  const newFile = await FileModel.create({
    fileId,
    name: req.file.originalname,
    size: req.file.size,
    uploadedAt: new Date(),
  });
  res.json({ message: "File uploaded", task_id: fileId, mongoId: newFile._id });
});

// View files
app.get("/api/files", authMiddleware, async (req, res) => {
  const files = await FileModel.find().sort({ uploadedAt: -1 });
  res.json(files);
});

// View single file
app.get("/api/view/:fileId", authMiddleware, async (req, res) => {
  const file = await FileModel.findOne({ fileId: req.params.fileId });
  if (!file) return res.status(404).json({ error: "File not found" });
  res.json(file);
});

// Delete file
app.delete("/api/delete/:fileId", authMiddleware, async (req, res) => {
  const deleted = await FileModel.deleteOne({ fileId: req.params.fileId });
  if (!deleted.deletedCount) return res.status(404).json({ error: "File not found" });
  res.json({ message: "File deleted" });
});

// Run all analyses
app.post("/api/analyze/:fileId", authMiddleware, async (req, res) => {
  const { query } = req.body;
  const file = await FileModel.findOne({ fileId: req.params.fileId });
  if (!file) return res.status(404).json({ error: "File not found" });

  const FASTAPI_URL = "http://fastapi:8000"; // use Docker service name if inside Docker
  const endpoints = [
    { type: "analyze", url: `${FASTAPI_URL}/analyze` },
    { type: "investment", url: `${FASTAPI_URL}/investment` },
    { type: "risk", url: `${FASTAPI_URL}/risk` },
    { type: "verify", url: `${FASTAPI_URL}/verify` },
  ];

  try {
    const results = await Promise.all(
      endpoints.map(async (ep) => {
        try {
          const formData = new FormData();
          formData.append("query", query || "");
          const response = await axios.post(ep.url, formData, {
            headers: formData.getHeaders(),
            timeout: 300000,
          });
          return { type: ep.type, status: "completed", analysis: response.data };
        } catch (err) {
          return { type: ep.type, status: "failed", error: err.message };
        }
      })
    );

    // save analysis results in MongoDB
    file.analysisResults = results.reduce((acc, r) => {
      acc[r.type] = r;
      return acc;
    }, {});
    await file.save();

    res.json({ results });
  } catch (err) {
    res.status(500).json({ error: "Failed to run analyses", details: err.message });
  }
});

app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
