// src/pages/UploadPage.tsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  LinearProgress,
  CircularProgress,
  Stack,
  Chip,
  Card,
  CardContent,
  Collapse,
  IconButton
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { ExpandMore, ExpandLess } from "@mui/icons-material";

interface DocumentMeta {
  fileId: string;
  name: string;
  size: number;
  uploadedAt: string;
  analysisResults?: Record<string, any>; // object now
}

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [docs, setDocs] = useState<DocumentMeta[]>([]);
  const [uploading, setUploading] = useState(false);
  const [expanded, setExpanded] = useState<Record<string, string | null>>({});
  const [role, setRole] = useState<string>("viewer");
  const token = "devtoken123";
  const API_BASE = "http://localhost:5050/api";

  useEffect(() => {
    const userRole = localStorage.getItem("role") || "viewer";
    setRole(userRole);
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/files`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDocs(res.data);
      console.log("Docs: ", res.data);
    } catch (err: any) {
      console.error("Fetch files failed:", err.message);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 100 * 1024 * 1024) {
      alert("File exceeds 100MB limit");
      return;
    }
    setFile(f);
  };

  const uploadFile = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("query", "");

      const res = await axios.post(`${API_BASE}/upload/analyze`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });

      const newDoc: DocumentMeta = {
        fileId: res.data.task_id,
        name: file.name,
        size: file.size,
        uploadedAt: new Date().toISOString(),
      };

      setDocs((prev) => [newDoc, ...prev]);
      setFile(null);
    } catch (err: any) {
      console.error("Upload failed:", err.message);
      alert("Upload failed. Check network or server.");
    } finally {
      setUploading(false);
    }
  };

  const runAllAnalyses = async (doc: DocumentMeta) => {
  // Initialize all analysis types as pending
  const analysisTypes = ["analyze", "investment", "risk", "verify"];
  setDocs((prev) =>
    prev.map((d) =>
      d.fileId === doc.fileId
        ? {
            ...d,
            analysisResults: analysisTypes.reduce((acc, type) => {
              acc[type] = { type, status: "pending" };
              return acc;
            }, {} as Record<string, any>),
          }
        : d
    )
  );

  try {
    const res = await axios.post(
      `${API_BASE}/analyze/${doc.fileId}`,
      { query: "Analyze this financial document" },
      { headers: { Authorization: `Bearer ${token}` }, timeout: 300000 }
    );

    // Update each analysis result individually
    setDocs((prev: any) =>
      prev.map((d: any) =>
        d.fileId === doc.fileId
          ? {
              ...d,
              analysisResults: Object.values(res.data.results).reduce(
                (acc: any, r: any) => {
                  acc[r.type] = r;
                  return acc;
                },
                {} as Record<string, any>
              ),
            }
          : d
      )
    );
  } catch (err: any) {
    // If request fails, mark all as failed
    setDocs((prev) =>
      prev.map((d) =>
        d.fileId === doc.fileId
          ? {
              ...d,
              analysisResults: analysisTypes.reduce((acc, type) => {
                acc[type] = { type, status: "failed", error: err.message };
                return acc;
              }, {} as Record<string, any>),
            }
          : d
      )
    );
  }
};


  const toggleExpand = (docId: string, type: string) => {
    setExpanded((prev) => ({ ...prev, [docId]: prev[docId] === type ? null : type }));
  };

  const downloadResults = (doc: DocumentMeta) => {
    if (!doc.analysisResults) return;
    const data = Object.values(doc.analysisResults)
      .filter((a: any) => a.status === "completed")
      .reduce((acc: any, a: any) => {
        acc[a.type] = a.analysis;
        return acc;
      }, {});

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${doc.name}-analysis.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const viewFile = async (doc: DocumentMeta) => {
    try {
      const res = await axios.get(`${API_BASE}/view/${doc.fileId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert(JSON.stringify(res.data, null, 2));
    } catch (err: any) {
      console.error("View file error:", err.message);
    }
  };

  const deleteFile = async (doc: DocumentMeta) => {
    if (!window.confirm(`Delete ${doc.name}?`)) return;
    try {
      await axios.delete(`${API_BASE}/delete/${doc.fileId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDocs((prev) => prev.filter((d) => d.fileId !== doc.fileId));
    } catch (err: any) {
      console.error("Delete file error:", err.message);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Paper sx={{ p: 4, borderRadius: 4 }}>
        <Stack spacing={4}>
          <Box textAlign="center">
            <Typography variant="h4" fontWeight="bold" gutterBottom color="primary">
              Upload Financial Document
            </Typography>
            <Button
              variant="contained"
              component="label"
              startIcon={<CloudUploadIcon />}
              sx={{ borderRadius: 3, px: 4, py: 1.5 }}
            >
              {file ? file.name : "Choose File"}
              <input type="file" hidden onChange={handleFileChange} />
            </Button>
            {file && (
              <Box mt={2}>
                <Button
                  variant="contained"
                  color="success"
                  onClick={uploadFile}
                  disabled={uploading}
                >
                  {uploading ? "Uploading..." : "Upload File"}
                </Button>
              </Box>
            )}
            {uploading && <LinearProgress sx={{ mt: 2 }} />}
          </Box>

          <Box>
            <Typography variant="h6">Uploaded Documents ({docs.length})</Typography>
            <Stack spacing={2} mt={2}>
              {docs.map((doc) => (
                <Card key={doc.fileId} variant="outlined" sx={{ borderRadius: 3 }}>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography fontWeight="medium">{doc.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {(doc.size / 1024 / 1024).toFixed(2)} MB •{" "}
                          {new Date(doc.uploadedAt).toLocaleDateString()}
                        </Typography>
                      </Box>
                      <Stack direction="row" spacing={1}>
                        <Button size="small" onClick={() => viewFile(doc)}>
                          View
                        </Button>
                        <Button size="small" onClick={() => runAllAnalyses(doc)}>
                          Run Analyses
                        </Button>
                        {role === "admin" && (
                          <>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => downloadResults(doc)}
                              disabled={
                                !doc.analysisResults ||
                                !Object.values(doc.analysisResults).some(
                                  (a: any) => a.status === "completed"
                                )
                              }
                            >
                              Download
                            </Button>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => deleteFile(doc)}
                            >
                              Delete
                            </Button>
                          </>
                        )}
                      </Stack>
                    </Stack>

                    {/* Analysis Results */}
                    {doc.analysisResults &&
                      Object.values(doc.analysisResults).map((a: any) => (
                        <Card key={a.type || "spinner"} variant="outlined" sx={{ mt: 2, borderRadius: 2 }}>
                          <CardContent>
                            <Stack direction="row" justifyContent="space-between" alignItems="center">
                              <Stack direction="row" spacing={1} alignItems="center">
                                <Chip label={a.type || "Analysis"} size="small" color="primary" />
                                <Chip
                                  label={a.status}
                                  size="small"
                                  color={
                                    a.status === "completed"
                                      ? "success"
                                      : a.status === "failed"
                                      ? "error"
                                      : "warning"
                                  }
                                />
                              </Stack>
                              {(a.status === "pending") && <CircularProgress size={20} />}
                              <IconButton size="small" onClick={() => toggleExpand(doc.fileId, a.type || "spinner")}>
                                {expanded[doc.fileId] === (a.type || "spinner") ? <ExpandLess /> : <ExpandMore />}
                              </IconButton>
                            </Stack>

                            <Collapse in={expanded[doc.fileId] === (a.type || "spinner")}>
                              {a.status === "completed" && (
                                <Box
                                  mt={1}
                                  p={1.5}
                                  sx={{
                                    backgroundColor: "#f5f5f5",
                                    borderRadius: 2,
                                    fontFamily: "monospace",
                                    whiteSpace: "pre-wrap",
                                    wordBreak: "break-word",
                                    maxHeight: 400,
                                    overflowY: "auto",
                                  }}
                                >
                                  {JSON.stringify(a.analysis, null, 2)}
                                </Box>
                              )}
                              {a.status === "failed" && (
                                <Typography color="error.main" mt={1}>
                                  {a.error}
                                </Typography>
                              )}
                            </Collapse>
                          </CardContent>
                        </Card>
                      ))}
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Box>
        </Stack>
      </Paper>
    </Container>
  );
};

export default UploadPage;
