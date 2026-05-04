import { useState } from 'react'

function App() {
  const [query, setQuery] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!query) return;
    setLoading(true);
    setSearched(true);
    try {
      const response = await fetch(`/api/v1/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setItems(data.items || []);
    } catch (error) {
      console.error('Search error:', error);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center text-gray-800">Armenian Market Parser</h1>

        <div className="mb-8 flex justify-center max-w-2xl mx-auto">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search products (e.g., milk)..."
            className="w-full px-4 py-3 rounded-l-lg border-2 border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 transition"
          />
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-8 py-3 rounded-r-lg hover:bg-blue-700 transition font-semibold shadow-lg"
          >
            Search
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {items.map((item) => (
              <div key={item.product_id} className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition flex flex-col">
                {item.image_url && (
                  <div className="h-48 mb-4 flex items-center justify-center bg-gray-50 rounded-lg overflow-hidden">
                    <img src={item.image_url} alt={item.canonical_name} className="max-h-full object-contain p-2" />
                  </div>
                )}
                <h2 className="text-xl font-bold mb-2 text-gray-800 capitalize line-clamp-2">{item.canonical_name}</h2>
                <p className="text-sm text-gray-500 mb-4 font-medium uppercase tracking-wider">{item.brand}</p>

                <div className="mt-auto border-t pt-4">
                  <div className="flex justify-between items-end mb-4">
                    <div>
                      <p className="text-xs text-gray-400 uppercase">Starting from</p>
                      <p className="text-2xl font-black text-blue-600">{item.min_price} <span className="text-sm font-normal">AMD</span></p>
                    </div>
                    <p className="text-sm text-gray-500">
                      <span className="font-bold text-gray-700">{item.stores_count}</span> {item.stores_count === 1 ? 'store' : 'stores'}
                    </p>
                  </div>

                  <div className="space-y-3 mt-4 bg-gray-50 p-3 rounded-lg">
                    {item.prices.map((price, idx) => (
                      <div key={idx} className="flex justify-between items-center text-sm border-b last:border-0 pb-2 last:pb-0 border-gray-200">
                        <span className="font-medium text-gray-700">{price.store_name}</span>
                        <div className="text-right">
                          <p className="font-bold text-gray-900">{price.price} AMD</p>
                          <a
                            href={price.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-500 hover:text-blue-700 hover:underline transition font-semibold"
                          >
                            View Deal →
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {items.length === 0 && !loading && searched && (
          <div className="text-center py-20 bg-white rounded-xl shadow-inner mt-8">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="9.172 9.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-xl text-gray-500">No products found for "{query}"</p>
            <p className="text-sm text-gray-400 mt-2">Try searching for something else like "milk" or "cheese"</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
