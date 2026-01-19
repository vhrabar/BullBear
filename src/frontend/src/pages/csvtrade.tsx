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
    
      const response = await fetch('/api/users/import/', {
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
     
      const response = await fetch('/api/users/export/', {
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
      <div className="csv-container">
        <div className="csv-header">
          <h1>Uvoz i izvoz transakcija</h1>
          <p>Upravljajte transakcijama putem CSV datoteka sinkroniziranih s bazom</p>
        </div>

        <div className="csv-content">
          <div className="csv-section">
            <div className="section-icon">📥</div>
            <h2>Uvezi transakcije</h2>
            
            <div className="csv-format-info">
              <h3>Potreban format (Pandas schema):</h3>
              <code>email,portfolio_name,instrument_symbol,type,quantity,price</code>
              <p className="format-example">Primjer (buy/sell):</p>
              <code className="example">
                korisnik@email.com,MojPortfelj,AAPL,buy,10,185.50
              </code>
            </div>

            <div className="upload-area">
              <label htmlFor="csv-upload" className="upload-label">
                <div className="upload-content">
                  <span className="upload-icon">📄</span>
                  <span className="upload-text">
                    {importFile ? importFile.name : 'Odaberite CSV datoteku'}
                  </span>
                </div>
              </label>
              <input
                type="file"
                id="csv-upload"
                accept=".csv"
                onChange={handleFileChange}
                className="file-input"
              />
            </div>

            <button 
              onClick={handleImport} 
              className="action-btn import-btn"
              disabled={loading || !importFile}
            >
              {loading ? 'Slanje...' : 'Učitaj na server'}
            </button>

            {uploadStatus.message && (
              <p className={`status-message ${uploadStatus.type}`}>
                {uploadStatus.message}
              </p>
            )}
          </div>

          <div className="divider">ili</div>

          <div className="csv-section">
            <div className="section-icon">📤</div>
            <h2>Preuzmi transakcije</h2>
            <p>Izvezite sve vaše transakcije iz baze u CSV datoteku.</p>

            <button onClick={handleExport} className="action-btn export-btn">
              Generiraj CSV izvoz
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CsvTrade;

