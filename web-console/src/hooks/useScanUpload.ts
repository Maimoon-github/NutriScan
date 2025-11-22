import { useMutation } from '@tanstack/react-query';
import { scanAPI, type UploadScanParams } from '../lib/api';

export const useScanUpload = () => {
  return useMutation({
    mutationFn: scanAPI.uploadScan,
    retry: 1,
  });
};
