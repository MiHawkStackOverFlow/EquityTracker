'use client';

import { useGetWatchlistQuery } from '@/store/watchlistApi';

export default function WatchlistPage() {
  const { data, isLoading, isError } = useGetWatchlistQuery();

  if (isLoading) return <main className="p-6">Loading…</main>;
  if (isError)   return <main className="p-6 text-red-600">Failed to load.</main>;

  return (
    <main className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Watchlist</h1>
      <div className="overflow-x-auto rounded-xl border">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr className="text-left">
              <th className="p-3">Symbol</th>
              <th className="p-3">Name</th>
              <th className="p-3">Price</th>
              <th className="p-3">P/E</th>
              <th className="p-3">Market Cap</th>
              <th className="p-3">Exchange</th>
              <th className="p-3">Created</th>
            </tr>
          </thead>
          <tbody>
            {
              data?.map(row => (
                <tr key={row.id} className="border-t">
                  <td className="p-3 font-medium">{row.symbol}</td>
                  <td className="p-3">{row.name}</td>
                  <td className="p-3">{row.price?.toLocaleString()}</td>
                  <td className="p-3">{row.pe_ratio}</td>
                  <td className="p-3">{Intl.NumberFormat('en', { notation: 'compact' }).format(row.market_cap)}</td>
                  <td className="p-3">{row.exchange}</td>
                  <td className="p-3 text-gray-500">
                    {new Date(row.created_at).toLocaleString()}
                  </td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
    </main>
  );
}
