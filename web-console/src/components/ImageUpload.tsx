import { useEffect, useRef, useState } from 'react';
import { useImageDropzone } from '../hooks/useImageDropzone';
import { useScanUploadExtended, type UploadStage } from '../hooks/useScanUpload';
import { useTranslation } from 'react-i18next';

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  isUploading: boolean;
  errorType?: 'validation' | 'retryable' | 'offline';
  onRetry?: () => Promise<void>;
}

export const ImageUpload = ({ onImageSelect, isUploading, errorType, onRetry }: ImageUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslation();
  const { getStage } = useScanUploadExtended();
  const [online, setOnline] = useState<boolean>(navigator.onLine);
  const [stage, setStage] = useState<UploadStage>('idle');
  const sampleImages = [
    '/samples/label1.jpg',
    '/samples/label2.jpg',
    '/samples/label3.jpg',
  ];

  useEffect(() => {
    const handleOnline = () => setOnline(true);
    const handleOffline = () => setOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    const id = setInterval(() => setStage(getStage()), 200);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(id);
    };
  }, [getStage]);
  
  const { isDragging, error, handleDrop, handleDragOver, handleDragLeave, handleFileInput } = 
    useImageDropzone({ onDrop: onImageSelect });

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">NutriScan QA Console</h1>
        <p className="text-gray-700">{t('upload.title') || 'Upload a food label image for instant analysis'}</p>
      </div>

      {!online && (
        <div className="max-w-2xl mx-auto mb-6 p-3 bg-yellow-100 border border-yellow-300 rounded">
          <p className="text-sm text-yellow-900">{t('upload.offlineBanner') || 'You are offline. Use a sample image to demo.'}</p>
        </div>
      )}

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-4 border-dashed rounded-xl p-12 text-center transition-all ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400 bg-white'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp"
          onChange={handleFileInput}
          className="hidden"
          disabled={isUploading}
        />

        <div className="space-y-4">
          <div className="text-6xl">📸</div>
          
          {isUploading ? (
            <div className="space-y-3">
              <div className="w-full bg-gray-200 rounded h-2 overflow-hidden">
                <div
                  className={`h-2 transition-all ${
                    stage === 'uploading' ? 'w-1/3 bg-blue-600' : stage === 'processing' ? 'w-2/3 bg-indigo-600' : 'w-full bg-green-600'
                  }`}
                />
              </div>
              <p className="text-gray-700 font-medium">
                {stage === 'uploading' && (t('upload.stages.uploading') || 'Uploading')}
                {stage === 'processing' && (t('upload.stages.processing') || 'Processing')}
                {stage === 'analyzing' && (t('upload.stages.analyzing') || 'Analyzing')}
              </p>
            </div>
          ) : (
            <>
              <div>
                <p className="text-lg text-gray-700 mb-2">
                  Drag and drop your image here, or
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Browse Files
                </button>
              </div>
              
              <p className="text-sm text-gray-500">
                Supported: .jpg, .jpeg, .png, .webp • Max size: 10MB
              </p>
              {online === false && (
                <div className="mt-4">
                  <p className="text-sm text-gray-700 mb-2">{t('upload.sampleImages') || 'Sample Images'}</p>
                  <div className="flex gap-3 justify-center">
                    {sampleImages.map((src) => (
                      <button
                        key={src}
                        onClick={() => {
                          // Fetch the sample image and convert to File
                          fetch(src)
                            .then((r) => r.blob())
                            .then((blob) => {
                              const file = new File([blob], src.split('/').pop() || 'sample.jpg', { type: blob.type });
                              onImageSelect(file);
                            });
                        }}
                        className="border rounded overflow-hidden hover:shadow"
                        title="Use sample"
                      >
                        <img src={src} alt="sample" className="h-16 w-16 object-cover" />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm font-medium">{error}</p>
          </div>
        )}
      </div>

      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">API Endpoint</h3>
        <code className="text-sm text-blue-700">POST http://127.0.0.1:8000/api/v1/scan/</code>
      </div>
      {!isUploading && errorType === 'retryable' && (
        <div className="mt-4 text-center">
          <button
            onClick={() => onRetry?.().catch(() => {})}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            {t('upload.retry') || 'Retry Upload'}
          </button>
        </div>
      )}
    </div>
  );
};
