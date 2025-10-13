import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export type WatchItem = {
  id: number;
  symbol: string;
  name: string;
  market_cap: number;
  pe_ratio: number;
  price: number;
  currency: string;
  exchange: string;
  created_at: string; // ISO
};

// (optional) use NEXT_PUBLIC_API_BASE, else default to your EC2
const baseUrl = process.env.NEXT_PUBLIC_API_BASE ?? 'http://35.182.180.174:8000';

export const watchlistApi = createApi({
  reducerPath: 'watchlistApi',
  baseQuery: fetchBaseQuery({ baseUrl }),
  tagTypes: ['Watchlist'],
  endpoints: (b) => ({
    getWatchlist: b.query<WatchItem[], void>({
      query: () => '/watchlist',
      providesTags: ['Watchlist'],
    }),
  })
});

export const { useGetWatchlistQuery } = watchlistApi;
