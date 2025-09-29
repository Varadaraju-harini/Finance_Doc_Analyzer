// mongodb.js
import mongoose from "mongoose";

const MONGO_URI = process.env.MONGO_URI || "mongodb://harini_027:ItMxkR6JmeRuLdTC@db:27017/farmd?authSource=admin"; // if using docker-compose service name

mongoose.connect(MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

mongoose.connection.on("connected", () => {
  console.log("MongoDB connected successfully");
});

mongoose.connection.on("error", (err) => {
  console.error("MongoDB connection error:", err);
});


const fileSchema = new mongoose.Schema({
  fileId: { type: String, required: true },
  name: String,
  size: Number,
  uploadedAt: { type: Date, default: Date.now },
  analysisResults: { type: Object, default: {} }, // store all analysis results
});

export const FileModel = mongoose.model("File", fileSchema);
