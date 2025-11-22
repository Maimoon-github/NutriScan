import { useCallback, useState } from 'react';

interface UseImageDropzoneProps {
  onDrop: (file: File) => void;
  maxSizeMB?: number;
}

export const useImageDropzone = ({ onDrop, maxSizeMB = 10 }: UseImageDropzoneProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): boolean => {
    setError(null);

    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file');
      return false;
    }

    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      setError(`File size must be less than ${maxSizeMB}MB`);
      return false;
    }

    return true;
  };

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file && validateFile(file)) {
        onDrop(file);
      }
    },
    [onDrop]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file && validateFile(file)) {
        onDrop(file);
      }
    },
    [onDrop]
  );

  return {
    isDragging,
    error,
    handleDrop,
    handleDragOver,
    handleDragLeave,
    handleFileInput,
  };
};
