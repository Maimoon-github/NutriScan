import { useRef } from 'react';
import { useImageDropzone } from '../hooks/useImageDropzone';

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  isUploading: boolean;
}

export const ImageUpload = ({ onImageSelect, isUploading }: ImageUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { isDragging, error, handleDrop, handleDragOver, handleDragLeave, handleFileInput } = 
    useImageDropzone({ onDrop: onImageSelect });

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">NutriScan QA Console</h1>
        <p className="text-gray-600">Upload a food label image for instant analysis</p>
      </div>

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
            <div className="space-y-2">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-600 font-medium">Analyzing image...</p>
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
    </div>
  );
};
