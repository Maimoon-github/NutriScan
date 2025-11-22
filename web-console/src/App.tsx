import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ImageUpload } from './components/ImageUpload';
import { ScanResults } from './components/ScanResults';
import { useScanUpload } from './hooks/useScanUpload';
import type { ScanResponse } from './types/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const { mutate: uploadScan, isPending, isError, error } = useScanUpload();

  const handleImageSelect = (file: File) => {
    uploadScan(
      { file },
      {
        onSuccess: (data) => {
          setScanResult(data);
        },
      }
    );
  };

  const handleReset = () => {
    setScanResult(null);
  };

  if (scanResult) {
    return <ScanResults result={scanResult} onReset={handleReset} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <ImageUpload onImageSelect={handleImageSelect} isUploading={isPending} />
      
      {isError && (
        <div className="max-w-2xl mx-auto mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="font-semibold text-red-900 mb-1">Upload Failed</h3>
          <p className="text-red-700 text-sm">
            {error instanceof Error ? error.message : 'An error occurred. Please try again.'}
          </p>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
