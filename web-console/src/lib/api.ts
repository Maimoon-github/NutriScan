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
  image: File;
  profile?: UserProfile;
}

export const scanAPI = {
  uploadScan: async ({ image, profile }: UploadScanParams): Promise<ScanResponse> => {
    const formData = new FormData();
    // Contract: image field for file upload
    formData.append('image', image);

    // Optional profile JSON per contract
    if (profile) {
      formData.append('profile', JSON.stringify(profile));
    }

    const response = await api.post<ScanResponse>('/api/v1/scan/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
};
