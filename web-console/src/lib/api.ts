import axios from 'axios';
import type { ScanResponse, UserProfile } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/json',
  },
});

export interface UploadScanParams {
  file: File;
  userProfile?: UserProfile;
}

export const scanAPI = {
  uploadScan: async ({ file, userProfile }: UploadScanParams): Promise<ScanResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (userProfile) {
      formData.append('user_profile', JSON.stringify(userProfile));
    }

    const response = await api.post<ScanResponse>('/api/v1/scan/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
};
