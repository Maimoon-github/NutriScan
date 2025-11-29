import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { scanAPI, type UploadScanParams } from '../lib/api';
import type { ScanResponse } from '../types/api';

export const useScanUpload = () => {
  return useMutation({
    mutationFn: scanAPI.uploadScan,
    retry: 1,
  });
};

export type UploadStage = 'idle' | 'uploading' | 'processing' | 'analyzing';

export function useScanUploadExtended() {
  let stage: UploadStage = 'idle';

  const upload = async ({ file }: { file: File }) => {
    if (!navigator.onLine) {
      throw new Error('offline');
    }
    stage = 'uploading';
    const formData = new FormData();
    formData.append('image', file);
    try {
      const res = await axios.post('/api/scan/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: () => {
          stage = 'processing';
        },
      });
      stage = 'analyzing';
      return res.data as ScanResponse;
    } catch (e: any) {
      if (axios.isAxiosError(e) && e.response) {
        const status = e.response.status;
        if (status === 400) {
          throw new Error('validation');
        }
        // Treat 500+ as retryable
        throw new Error('retryable');
      }
      // Network error
      throw new Error('retryable');
    } finally {
      stage = 'idle';
    }
  };

  const mutation = useMutation<ScanResponse, Error, { file: File }>(upload);

  const retryWithBackoff = async (attempts = 3) => {
    let delay = 500;
    for (let i = 0; i < attempts; i++) {
      try {
        await mutation.retry();
        return;
      } catch (e) {
        await new Promise((r) => setTimeout(r, delay));
        delay = Math.min(delay * 2, 4000);
      }
    }
    throw new Error('retry_failed');
  };

  return { ...mutation, retryWithBackoff, getStage: () => stage };
};
