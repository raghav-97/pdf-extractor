// App.jsx
import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:3001/api';

function App() {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      const response = await axios.post(`${API_URL}/process-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setFormData(response.data);
    } catch (err) {
      setError('Error processing PDF: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl pt-6 lg:pt-16">
      <h1 className="text-2xl font-bold mb-4">PDF Data Extractor</h1>

      {/* File Upload */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Upload PDF
        </label>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          disabled={loading}
          className="w-full border rounded p-2"
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="mb-4 text-center">
          Processing...
        </div>
      )}

      {/* Form Fields */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Name
          </label>
          <input
            type="text"
            value={formData.name?.value || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            className="w-full border rounded p-2"
            placeholder="Extracted name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Phone Number
          </label>
          <input
            type="text"
            value={formData.phone?.value || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
            className="w-full border rounded p-2"
            placeholder="Extracted phone number"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Address
          </label>
          <input
            type="text"
            value={formData.address?.value || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
            className="w-full border rounded p-2"
            placeholder="Extracted address"
          />
        </div>
      </div>
    </div>
  );
}

export default App;