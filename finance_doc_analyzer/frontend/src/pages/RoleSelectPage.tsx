// pages/RoleSelectPage.tsx
import React from "react"
import { useNavigate } from "react-router-dom"
import { Container, Box, Typography, Button, Paper } from "@mui/material"
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings"
import VisibilityIcon from "@mui/icons-material/Visibility"

export const RoleSelectPage: React.FC = () => {
  const navigate = useNavigate()

  const handleRole = (role: "admin" | "viewer") => {
    localStorage.setItem("role", role)
    navigate("/upload")
  }

  return (
    <Container maxWidth="sm" sx={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center" }}>
      <Paper
        elevation={6}
        sx={{
          p: 6,
          borderRadius: 4,
          textAlign: "center",
          background: "linear-gradient(135deg, #e3f2fd, #fce4ec)",
        }}
      >
        <Typography variant="h4" fontWeight="bold" gutterBottom color="primary">
          Choose Your Role
        </Typography>
        <Typography variant="body1" color="text.secondary" mb={4}>
          Select a role to continue
        </Typography>

        <Box display="flex" justifyContent="center" gap={3}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<AdminPanelSettingsIcon />}
            sx={{ px: 4, py: 1.5, borderRadius: 3, textTransform: "none" }}
            onClick={() => handleRole("admin")}
          >
            Admin
          </Button>
          <Button
            variant="contained"
            color="success"
            size="large"
            startIcon={<VisibilityIcon />}
            sx={{ px: 4, py: 1.5, borderRadius: 3, textTransform: "none" }}
            onClick={() => handleRole("viewer")}
          >
            Viewer
          </Button>
        </Box>
      </Paper>
    </Container>
  )
}
