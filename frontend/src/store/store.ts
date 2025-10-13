import { configureStore } from '@reduxjs/toolkit';
import { watchlistApi } from './watchlistApi';

export const store = configureStore({
  reducer: {[watchlistApi.reducerPath]: watchlistApi.reducer},
  middleware: (gDM) => gDM().concat(watchlistApi.middleware)
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
