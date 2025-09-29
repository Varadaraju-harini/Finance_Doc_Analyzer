import mongoose from 'mongoose'

export const FileMeta = mongoose.model('FileMeta', new mongoose.Schema({
  name: String,
  size: Number,
  path: String,
  mimetype: String,
  uploadedAt: { type: Date, default: Date.now },
}))
