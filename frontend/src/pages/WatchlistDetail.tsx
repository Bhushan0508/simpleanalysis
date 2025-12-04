import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useWatchlistStore } from '../store/watchlistStore';
import { stocksApi } from '../api/stocks';
import type { StockSearchResult } from '../types';

export default function WatchlistDetail() {
  const { id } = useParams<{ id: string }>();
  const {
    currentWatchlist,
    loading,
    error,
    fetchWatchlist,
    addStock,
    removeStock,
    clearError,
  } = useWatchlistStore();

  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<StockSearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    if (id) {
      fetchWatchlist(id);
    }
  }, [id]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const results = await stocksApi.search(searchQuery);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleAddStock = async (stock: StockSearchResult) => {
    if (!id) return;

    try {
      await addStock(id, {
        symbol: stock.symbol,
        name: stock.name,
      });
      setShowAddModal(false);
      setSearchQuery('');
      setSearchResults([]);
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleRemoveStock = async (symbol: string) => {
    if (!id) return;

    if (window.confirm(`Remove ${symbol} from watchlist?`)) {
      try {
        await removeStock(id, symbol);
      } catch (error) {
        // Error is handled by store
      }
    }
  };

  if (loading && !currentWatchlist) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading watchlist...</p>
        </div>
      </div>
    );
  }

  if (!currentWatchlist) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Watchlist not found</p>
          <Link to="/watchlists" className="text-blue-600 hover:text-blue-700">
            Back to Watchlists
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/watchlists"
            className="text-blue-600 hover:text-blue-700 mb-4 inline-flex items-center"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Watchlists
          </Link>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{currentWatchlist.name}</h1>
              {currentWatchlist.description && (
                <p className="mt-2 text-gray-600">{currentWatchlist.description}</p>
              )}
              <p className="mt-2 text-sm text-gray-500">
                {currentWatchlist.stocks.length} stocks
              </p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Add Stock
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded flex justify-between items-center">
            <span>{error}</span>
            <button
              onClick={clearError}
              className="text-red-700 hover:text-red-900 font-bold"
            >
              ×
            </button>
          </div>
        )}

        {/* Stocks Table */}
        {currentWatchlist.stocks.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-600 mb-4">No stocks in this watchlist yet</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Add your first stock
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Added Date
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentWatchlist.stocks.map((stock) => (
                  <tr key={stock.symbol} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{stock.symbol}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">{stock.name || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {new Date(stock.added_at).toLocaleDateString('en-IN')}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleRemoveStock(stock.symbol)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Add Stock Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Add Stock</h3>

              <div className="mb-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Search by symbol or name..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={handleSearch}
                    disabled={searching || !searchQuery.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {searching ? 'Searching...' : 'Search'}
                  </button>
                </div>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Search Results:</h4>
                  <div className="space-y-2">
                    {searchResults.map((result) => (
                      <div
                        key={result.symbol}
                        className="flex justify-between items-center p-3 border border-gray-200 rounded-md hover:bg-gray-50"
                      >
                        <div>
                          <div className="font-medium text-gray-900">{result.symbol}</div>
                          <div className="text-sm text-gray-600">{result.name}</div>
                          <div className="text-xs text-gray-500">
                            {result.exchange} • {result.type}
                          </div>
                        </div>
                        <button
                          onClick={() => handleAddStock(result)}
                          disabled={loading}
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
                        >
                          Add
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {searchQuery && searchResults.length === 0 && !searching && (
                <p className="text-sm text-gray-600 mb-4">No results found. Try a different search term.</p>
              )}

              <div className="flex justify-end">
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setSearchQuery('');
                    setSearchResults([]);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
