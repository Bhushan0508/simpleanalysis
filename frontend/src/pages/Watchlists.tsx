import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useWatchlistStore } from '../store/watchlistStore';

export default function Watchlists() {
  const {
    watchlists,
    loading,
    error,
    fetchWatchlists,
    deleteWatchlist,
    createFromIndex,
    uploadExcel,
    clearError,
  } = useWatchlistStore();

  const [showIndexModal, setShowIndexModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState('nifty50');
  const [customName, setCustomName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    fetchWatchlists();
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
      try {
        await deleteWatchlist(id);
      } catch (error) {
        // Error is handled by store
      }
    }
  };

  const handleCreateFromIndex = async () => {
    try {
      await createFromIndex(selectedIndex, customName || undefined);
      setShowIndexModal(false);
      setCustomName('');
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleUploadExcel = async () => {
    if (!selectedFile) return;

    try {
      await uploadExcel(selectedFile, customName || undefined);
      setShowUploadModal(false);
      setSelectedFile(null);
      setCustomName('');
    } catch (error) {
      // Error is handled by store
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Watchlists</h1>
          <p className="mt-2 text-gray-600">Manage your stock watchlists</p>
        </div>

        {/* Action Buttons */}
        <div className="mb-6 flex flex-wrap gap-4">
          <button
            onClick={() => setShowIndexModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Create from Index
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          >
            Upload Excel
          </button>
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

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading watchlists...</p>
          </div>
        )}

        {/* Watchlists Grid */}
        {!loading && watchlists.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600 mb-4">No watchlists yet</p>
            <button
              onClick={() => setShowIndexModal(true)}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Create your first watchlist
            </button>
          </div>
        )}

        {!loading && watchlists.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {watchlists.map((watchlist) => (
              <div
                key={watchlist.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {watchlist.name}
                      </h3>
                      {watchlist.is_default && (
                        <span className="inline-block mt-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          Default
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => handleDelete(watchlist.id, watchlist.name)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>

                  {watchlist.description && (
                    <p className="text-sm text-gray-600 mb-4">{watchlist.description}</p>
                  )}

                  <div className="mb-4">
                    <p className="text-2xl font-bold text-gray-900">
                      {watchlist.stocks.length}
                    </p>
                    <p className="text-sm text-gray-600">stocks</p>
                  </div>

                  <div className="text-xs text-gray-500 mb-4">
                    Updated {formatDate(watchlist.updated_at)}
                  </div>

                  <Link
                    to={`/watchlists/${watchlist.id}`}
                    className="block w-full text-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Index Modal */}
        {showIndexModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h3 className="text-lg font-semibold mb-4">Create from Index</h3>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Index
                </label>
                <select
                  value={selectedIndex}
                  onChange={(e) => setSelectedIndex(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="nifty50">Nifty 50</option>
                  <option value="banknifty">Bank Nifty</option>
                  <option value="nifty100">Nifty 100</option>
                  <option value="niftynext50">Nifty Next 50</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Name (Optional)
                </label>
                <input
                  type="text"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  placeholder="Leave empty for default name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowIndexModal(false);
                    setCustomName('');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateFromIndex}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h3 className="text-lg font-semibold mb-4">Upload Excel File</h3>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Excel File
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Supported formats: .xlsx, .xls, .csv
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Watchlist Name (Optional)
                </label>
                <input
                  type="text"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  placeholder="Leave empty to use filename"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                    setCustomName('');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUploadExcel}
                  disabled={!selectedFile || loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
