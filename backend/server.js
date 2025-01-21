const express = require('express');
const multer = require('multer');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3001;

// Configure multer for file upload
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/')
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname)
  }
});

const upload = multer({ storage: storage });

// Enable CORS
app.use(cors());

// Ensure uploads directory exists
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

app.post('/api/process-pdf', upload.single('pdf'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  } 

  const pythonScript = path.join(__dirname, 'python', 'pdf_parser.py');
  const pythonProcess = spawn('python', [pythonScript, req.file.path]);
  
  let dataString = '';
  let errorString = '';

  pythonProcess.stdout.on('data', (data) => {
    dataString += data.toString();
    console.log(dataString)
  });

  pythonProcess.stderr.on('data', (data) => {
    errorString += data.toString();
    if (dataString.trim().length > 0) {
      console.log(`Python Output: ${data}`);
    }
  });

  pythonProcess.on('close', (code) => {
    // Clean up the uploaded file
    fs.unlink(req.file.path, (err) => {
      if (err) console.error('Error deleting file:', err);
    });

    if (code !== 0) {
      return res.status(500).json({ 
        error: 'PDF processing failed', 
        details: errorString 
      });
    }

    try {
      // Try to parse the Python output as JSON
      const result = JSON.parse(dataString.trim());
      
      // Check if we got an error from Python
      if (result.error) {
        return res.status(500).json({ error: result.error });
      }
      
      res.json(result);
    } catch (e) {
      console.error('Parse error:', e);
      console.error('Raw output:', dataString);
      res.status(500).json({ 
        error: 'Invalid response from parser',
        details: dataString
      });
    }
  });
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something broke!', details: err.message });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});