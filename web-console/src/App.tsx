import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { setLanguage } from './i18n';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as Sentry from '@sentry/react';
import { ImageUpload } from './components/ImageUpload';
import { ScanResults } from './components/ScanResults';
import { useScanUploadExtended } from './hooks/useScanUpload';
import { trackInteraction } from './lib/observability';
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
  const { mutate: uploadScan, isPending, isError, error, retryWithBackoff } = useScanUploadExtended();
  const { t, i18n } = useTranslation();

  const handleImageSelect = (file: File) => {
    // Track scan started event
    trackInteraction('scan_started', 'image_upload');
    
    uploadScan(
      { file },
      {
        onSuccess: (data) => {
          setScanResult(data);
          // Track successful scan
          trackInteraction('scan_completed', 'analysis_view', {
            traffic_light: data.traffic_light,
            status: data.status
          });
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
      <div className="max-w-2xl mx-auto mb-4 flex items-center justify-end gap-2">
        <label className="text-sm text-gray-800">{t('Language') || 'Language'}</label>
        <select
          className="border rounded px-2 py-1 text-sm"
          value={i18n.language}
          onChange={(e) => setLanguage(e.target.value as 'en' | 'ur')}
        >
          <option value="en">English</option>
          <option value="ur">اردو</option>
        </select>
      </div>
      <ImageUpload
        onImageSelect={handleImageSelect}
        isUploading={isPending}
        errorType={error instanceof Error ? (error.message as 'validation' | 'retryable' | 'offline') : undefined}
        onRetry={() => retryWithBackoff()}
      />
      
      {isError && (
        <div className="max-w-2xl mx-auto mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="font-semibold text-red-900 mb-1">{t('Upload Failed') || 'Upload Failed'}</h3>
          <p className="text-red-700 text-sm">
            {error instanceof Error ? error.message : (t('errors.server') || 'An error occurred. Please try again.')}
          </p>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <Sentry.ErrorBoundary 
      fallback={({ resetError }: { error: Error; resetError: () => void }) => (
        <div className="min-h-screen flex items-center justify-center bg-red-50">
          <div className="max-w-md p-6 bg-white rounded-lg shadow-lg">
            <h2 className="text-xl font-bold text-red-900 mb-2">Something went wrong</h2>
            <p className="text-red-700 mb-4">
              We apologize for the inconvenience. The error has been reported to our team.
            </p>
            <button
              onClick={resetError}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Try again
            </button>
          </div>
        </div>
      )}
      beforeCapture={(scope: any) => {
        scope.setTag('component', 'App')
      }}
    >
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </Sentry.ErrorBoundary>
  );
}

export default App;
