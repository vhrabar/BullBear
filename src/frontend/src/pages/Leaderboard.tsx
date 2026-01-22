import { useState, useEffect } from 'react'
import axios from 'axios'
import '../styles/Leaderboard.css'

interface LeaderboardEntry {
  rank: number
  username: string
  portfolio_name: string
  total_value: string
}

interface LeaderboardResponse {
  count: number
  next: string | null
  previous: string | null
  results: LeaderboardEntry[]
}

type TimeFilter = 'all' | '1D' | '1W' | '1M' | '3M' | '1Y'

function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [pagination, setPagination] = useState({
    count: 0,
    next: null as string | null,
    previous: null as string | null,
  })
  const [activeFilter, setActiveFilter] = useState<TimeFilter>('all')

  const timeFilters: { label: string; value: TimeFilter }[] = [
    { label: 'Sve', value: 'all' },
    { label: '1 dan', value: '1D' },
    { label: '1 tjedan', value: '1W' },
    { label: '1 mjesec', value: '1M' },
    { label: '3 mjeseca', value: '3M' },
    { label: '1 godina', value: '1Y' },
  ]

  const getToken = () => {
    return localStorage.getItem('token') || ''
  }

  const fetchLeaderboard = async (page: number = 1, filter: TimeFilter = 'all') => {
    try {
      setLoading(true)
      const token = getToken()

      const params = new URLSearchParams()
      params.append('page', page.toString())

      if (filter !== 'all') {
        params.append('time', filter)
      }

      const response = await axios.get<LeaderboardResponse>(
        '/api/leaderboard/',
        {
          params: Object.fromEntries(params),
          headers: token ? { Authorization: `Token ${token}` } : {},
        }
      )

      setEntries(response.data.results)
      setPagination({
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
      })
      setCurrentPage(page)
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      setEntries([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLeaderboard(1, activeFilter)
  }, [activeFilter])

  const handleFilterChange = (filter: TimeFilter) => {
    setActiveFilter(filter)
    setCurrentPage(1)
  }

  const getMedalColor = (rank: number): string => {
    if (rank === 1) return 'gold'
    if (rank === 2) return 'silver'
    if (rank === 3) return 'bronze'
    return 'default'
  }

  const getMedalEmoji = (rank: number): string => {
    if (rank === 1) return '🥇'
    if (rank === 2) return '🥈'
    if (rank === 3) return '🥉'
    return ''
  }

  return (
    <div className="leaderboard-page">

      <div className="leaderboard-container">
        <div className="leaderboard-header">
          <h1>Ljestvica najboljih</h1>
          <p>Rangiranje portfelja prema ukupnoj vrijednosti</p>
        </div>

        <div className="filter-section">
          <h2>Vremenski interval</h2>
          <div className="filter-buttons">
            {timeFilters.map((filter) => (
              <button
                key={filter.value}
                onClick={() => handleFilterChange(filter.value)}
                className={`filter-btn ${activeFilter === filter.value ? 'active' : ''}`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Učitavanje ljestvice...</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="empty-state">
            <p>Nema dostupnih podataka na ljestvici</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table className="leaderboard-table">
                <thead>
                  <tr>
                    <th className="rank-col">Rang</th>
                    <th className="username-col">Korisnik</th>
                    <th className="portfolio-col">Portfelj</th>
                    <th className="value-col">Ukupna vrijednost</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry) => {
                    const medalColor = getMedalColor(entry.rank)
                    const medalEmoji = getMedalEmoji(entry.rank)

                    return (
                      <tr key={`${entry.rank}-${entry.username}`} className={`row-${medalColor}`}>
                        <td className="rank-col">
                          <div className="rank-cell">
                            {medalEmoji && <span className="medal">{medalEmoji}</span>}
                            <span className="rank-number">#{entry.rank}</span>
                          </div>
                        </td>
                        <td className="username-col">
                          <div className="username-cell">{entry.username}</div>
                        </td>
                        <td className="portfolio-col">
                          <div className="portfolio-cell">{entry.portfolio_name}</div>
                        </td>
                        <td className="value-col">
                          <div className="value-cell">
                            ${parseFloat(entry.total_value).toLocaleString('en-US', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <div className="pagination-section">
              <button
                onClick={() => fetchLeaderboard(currentPage - 1, activeFilter)}
                disabled={!pagination.previous}
                className="pagination-btn"
              >
                ← Prethodna
              </button>

              <div className="page-info">
                Stranica {currentPage} od {Math.ceil(pagination.count / 50)}
              </div>

              <button
                onClick={() => fetchLeaderboard(currentPage + 1, activeFilter)}
                disabled={!pagination.next}
                className="pagination-btn"
              >
                Sljedeća →
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Leaderboard