import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";

const qc = new QueryClient({ defaultOptions: { queries: { retry: 2, staleTime: 5 * 60 * 1000 } } });

const Home    = React.lazy(() => import("./pages/Home"));
const Results = React.lazy(() => import("./pages/Results"));
const Chat    = React.lazy(() => import("./pages/Chat"));
const Compare = React.lazy(() => import("./pages/Compare"));

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <React.Suspense fallback={<div className="min-h-screen bg-gray-950 flex items-center justify-center"><div className="w-8 h-8 border-2 border-blue-600/30 border-t-blue-500 rounded-full animate-spin"/></div>}>
          <Routes>
            <Route path="/"              element={<Home/>}/>
            <Route path="/repo/:repoId"  element={<Results/>}/>
            <Route path="/repo/:repoId/chat" element={<Chat/>}/>
            <Route path="/compare"       element={<Compare/>}/>
          </Routes>
        </React.Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
