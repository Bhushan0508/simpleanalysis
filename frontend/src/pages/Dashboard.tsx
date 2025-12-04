import { useAuthStore } from '../store/authStore';
import { useNavigate, Link } from 'react-router-dom';
import { authApi } from '../api/auth';

export default function Dashboard() {
  const { user, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuth();
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">SimpleAnalysis</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.username || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Dashboard</h2>
            <p className="text-gray-600 mb-6">
              Welcome to SimpleAnalysis - Stock Analysis Platform for Indian Markets
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Link to="/watchlists" className="bg-blue-50 p-4 rounded-lg hover:bg-blue-100 transition-colors">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">Watchlists</h3>
                <p className="text-sm text-blue-700">
                  Create and manage your stock watchlists
                </p>
                <p className="text-xs text-blue-600 mt-2 font-medium">View Watchlists →</p>
              </Link>

              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-green-900 mb-2">Stock Analysis</h3>
                <p className="text-sm text-green-700">
                  Analyze stocks with technical indicators
                </p>
                <p className="text-xs text-green-600 mt-2">Coming in Phase 3</p>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-purple-900 mb-2">Trade Tracking</h3>
                <p className="text-sm text-purple-700">
                  Track your trades and P&L
                </p>
                <p className="text-xs text-purple-600 mt-2">Coming in Phase 5</p>
              </div>

              <div className="bg-orange-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-orange-900 mb-2">Sector Rotation</h3>
                <p className="text-sm text-orange-700">
                  Analyze sector rotation trends
                </p>
                <p className="text-xs text-orange-600 mt-2">Coming in Phase 6</p>
              </div>
            </div>

            <div className="mt-8 bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">User Information</h3>
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Email</dt>
                  <dd className="text-sm text-gray-900">{user?.email}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Username</dt>
                  <dd className="text-sm text-gray-900">{user?.username}</dd>
                </div>
                {user?.full_name && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                    <dd className="text-sm text-gray-900">{user.full_name}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-sm font-medium text-gray-500">Account Created</dt>
                  <dd className="text-sm text-gray-900">
                    {user?.created_at && new Date(user.created_at).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
