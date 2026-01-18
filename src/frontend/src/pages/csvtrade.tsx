import React, { useState } from 'react';
import './CsvTrade.css';

function CsvTrade() {
  const [importFile, setImportFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<{ message: string; type: 'success' | 'error' | '' }>({ message: '', type: '' });
  const [loading, setLoading] = useState(false);

  
  const token = localStorage.getItem('token'); 

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
      setImportFile(file);
      setUploadStatus({ message: '', type: '' });
    } else {
      setUploadStatus({ message: 'Molimo odaberite ispravnu CSV datoteku', type: 'error' });
      setImportFile(null);
    }
  };

  const handleImport = async () => {
    if (!importFile) {
      setUploadStatus({ message: 'Molimo odaberite datoteku za učitavanje', type: 'error' });
      return;
    }

    setLoading(true);
    setUploadStatus({ message: 'Učitavanje na server...', type: '' });

    const formData = new FormData();
    formData.append('file', importFile);

    try {
    
      const response = await fetch('http://localhost:8000/api/users/import/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}` 
        },
        body: formData,
      });

      if (response.ok) {
        setUploadStatus({ message: `Uspješno uvezeno! Transakcije su dodane u portfelj.`, type: 'success' });
        setImportFile(null);
      } else {
        const errorData = await response.json();
        setUploadStatus({ message: `Greška: ${errorData.error || 'Neuspješan uvoz. Provjerite format CSV-a.'}`, type: 'error' });
      }
    } catch (error) {
      setUploadStatus({ message: 'Greška u komunikaciji s poslužiteljem.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      
      const response = await fetch('http://localhost:8000/api/users/export/', {
        method: 'GET',
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'bullbear_export.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Greška pri izvozu podataka s poslužitelja.');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Serverska greška pri pokušaju izvoza.');
    }
  };

  return (
    <div className="csv-page">
      <div className
