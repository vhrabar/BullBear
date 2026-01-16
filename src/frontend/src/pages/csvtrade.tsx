import { useState } from 'react'
import { Link } from 'react-router-dom'
import './CsvTrade.css'

function CsvTrade() {
  const [importFile, setImportFile] = useState<File | null>(null)
  const [includeInLeaderboard, setIncludeInLeaderboard] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string>('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type === 'text/csv') {
      setImportFile(file)
      setUploadStatus('')
    } else {
      setUploadStatus('Molimo odaberite CSV datoteku')
      setImportFile(null)
    }
  }

  const handleImport = async () => {
    if (!importFile) {
      setUploadStatus('Molimo odaberite datoteku za učitavanje')
      return
    }

    setUploadStatus('Učitavanje datoteke...')

    setTimeout(() => {
      setUploadStatus(`Uspješno učitano! ${importFile.name} - ${includeInLeaderboard ? 'Uključeno u ljestvicu' : 'Isključeno iz ljestvice'}`)
      setImportFile(null)
    }, 1500)
  }

  const handleExport = () => {
    const csvContent = `Data,Vrsta,Simbol,Količina,Cijena,Iznos
2024-01-15,Kupnja,AAPL,10,150.25,"1502.50"
2024-01-16,Prodaja,AAPL,5,152.00,"760.00"
2024-01-17,Kupnja,MSFT,8,380.50,"3044.00"
2024-01-18,Kupnja,VTSAX,20,95.30,"1906.00"
2024-01-19,Prodaja,MSFT,4,385.20,"1540.80"`

    const element = document.createElement('a')
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent))
    element.setAttribute('download', 'bullbear_transakcije.csv')
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="csv-page">
      <nav className="csv-nav">
        <div className="csv-nav-container">
          <Link to="/" className="csv-logo">
            <span className="logo-icon">📈</span>
            <span className="logo-text">BullBear</span>
          </Link>
          <div className="csv-nav-links">
            <Link to="/">Početna</Link>
            <Link to="/login">Prijava</Link>
          </div>
        </div>
      </nav>

      <div className="csv-container">
        <div className="csv-header">
          <h1>Uvoz i izvoz transakcija</h1>
          <p>Upravljajte vašim transakcijama preko CSV datoteka</p>
        </div>

        <div className="csv-content">
          <div className="csv-section">
            <div className="section-icon">📥</div>
            <h2>Uvezi transakcije</h2>
            <p>Učitajte vaše prethodne transakcije iz drugih brokera u CSV formatu</p>

            <div className="csv-format-info">
              <h3>Format CSV datoteke:</h3>
              <code>Data,Vrsta,Simbol,Količina,Cijena,Iznos</code>
              <p className="format-example">Primjer:</p>
              <code className="example">
                2024-01-15,Kupnja,AAPL,10,150.25,1502.50<br/>
                2024-01-16,Prodaja,AAPL,5,152.00,760.00
              </code>
            </div>

            <div className="upload-area">
              <label htmlFor="csv-upload" className="upload-label">
                <div className="upload-content">
                  <span className="upload-icon">📄</span>
                  <span className="upload-text">Kliknite za odabir ili povucite CSV datoteku</span>
                  <span className="upload-hint">Maksimalna veličina: 10MB</span>
                </div>
              </label>
              <input
                type="file"
                id="csv-upload"
                accept=".csv"
                onChange={handleFileChange}
                className="file-input"
              />
              {importFile && (
                <p className="file-selected">Odabrana datoteka: {importFile.name}</p>
              )}
            </div>

            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={includeInLeaderboard}
                  onChange={(e) => setIncludeInLeaderboard(e.target.checked)}
                />
                <span>Uključi transakcije u ljestvicu</span>
              </label>
              <p className="checkbox-hint">
                Ako je odabrano, vaše transakcije će biti vidljive na javnoj ljestvici i bit će uključene u rangiranje.
              </p>
            </div>

            <button onClick={handleImport} className="action-btn import-btn">
              Učitaj transakcije
            </button>

            {uploadStatus && (
              <p className={`status-message ${uploadStatus.includes('Uspješno') ? 'success' : 'error'}`}>
                {uploadStatus}
              </p>
            )}
          </div>

          <div className="divider">ili</div>

          <div className="csv-section">
            <div className="section-icon">📤</div>
            <h2>Preuzmi transakcije</h2>
            <p>Izvezite sve vaše transakcije u CSV format za sigurnosnu kopiju ili analizu</p>

            <div className="export-info">
              <h3>Što će biti izvezeno:</h3>
              <ul>
                <li>Sve transakcije iz vašeg portfelja</li>
                <li>Datumi, vrste, simbole, količine i cijene</li>
                <li>Izračunate iznose za svaku transakciju</li>
                <li>Vremensku posljednost</li>
              </ul>
            </div>

            <button onClick={handleExport} className="action-btn export-btn">
              Preuzmi kao CSV
            </button>
          </div>
        </div>

        <div className="csv-tips">
          <h3>Savjeti i napomene:</h3>
          <ul>
            <li>Koristite točan format CSV datoteke za uspješan uvoz</li>
            <li>Provjerite da su datumi u formatu YYYY-MM-DD</li>
            <li>Vrste transakcija: "Kupnja" ili "Prodaja"</li>
            <li>Količina i cijena trebaju biti brojevi (koristi decimalni separator .)</li>
            <li>Izvozene datoteke možete sigurno arhivirati kao sigurnosnu kopiju</li>
            <li>Privatne profila neće biti vidljive na ljestvici, čak i ako ste ih označili</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default CsvTrade