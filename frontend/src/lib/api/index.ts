// frontend/src/lib/api/index.ts
import { browser } from '$app/environment';
import type { BackgroundData, Document, Prompt, Settings } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api';


/**
 * Helper function to make authenticated API requests
 * Includes cookies and handles common error scenarios
 */
export async function fetchWithAuth(url: string, options = {}) {
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  try {
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    // Handle 401 Unauthorized errors (expired token, etc.)
    if (response.status === 401) {
      // Redirect to login if unauthorized
      window.location.href = '/login';
      throw new Error('Authentication required. Please log in again.');
    }
    
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}


// Base API request function
export async function apiRequest<T = any>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  // Ensure endpoint starts with a slash
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_BASE_URL}${path}`;
  
  // Default options
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    credentials: 'include' // Include cookies
  };
  
  // Add Authorization header if token exists
  if (browser) {
    const token = getAuthToken();
    if (token) {
      defaultOptions.headers = {
        ...defaultOptions.headers,
        'Authorization': `Bearer ${token}`
      };
    }
  }
  
  // Merge options
  const requestOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {})
    }
  };
  
  try {
    let response = await fetch(url, requestOptions);
    
    // Handle 401 Unauthorized (try token refresh)
    if (response.status === 401 && browser) {
      const refreshed = await refreshToken();
      
      if (refreshed) {
        // Get fresh token and retry
        const newToken = getAuthToken();
        if (newToken) {
          // Update Authorization header
          requestOptions.headers = {
            ...requestOptions.headers,
            'Authorization': `Bearer ${newToken}`
          };
          
          // Retry request
          response = await fetch(url, requestOptions);
        }
      }
    }
    
    // If still not ok, throw error
    if (!response.ok) {
      let errorMessage = `API error: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorData.detail || errorMessage;
      } catch (e) {
        try {
          errorMessage = await response.text() || errorMessage;
        } catch (textError) {
          // Ignore if we can't get text
        }
      }
      
      throw new Error(errorMessage);
    }
    
    // Parse response
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json() as T;
    }
    
    return response as unknown as T;
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    throw error;
  }
}

// Simplified API methods
export const api = {
  get: <T = any>(endpoint: string, options: RequestInit = {}) => 
    apiRequest<T>(endpoint, { ...options, method: 'GET' }),
    
  post: <T = any>(endpoint: string, data: any, options: RequestInit = {}) => 
    apiRequest<T>(endpoint, { 
      ...options, 
      method: 'POST',
      body: JSON.stringify(data)
    }),
    
  put: <T = any>(endpoint: string, data: any, options: RequestInit = {}) => 
    apiRequest<T>(endpoint, { 
      ...options, 
      method: 'PUT',
      body: JSON.stringify(data)
    }),
    
  delete: <T = any>(endpoint: string, options: RequestInit = {}) => 
    apiRequest<T>(endpoint, { ...options, method: 'DELETE' }),
    
  // Special method for file uploads
  upload: async <T = any>(endpoint: string, formData: FormData, options: RequestInit = {}) => {
    const token = getAuthToken();
    const headers: HeadersInit = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers,
      ...options
    });
  }
};

// Domain-specific API functions
export const authApi = {
  login: async (username: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'include'
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
        throw new Error(errorData?.detail || 'Invalid username or password');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  logout: async () => {
    try {
      await api.post('logout/', {});
      
      // Clear local storage
      if (browser) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
      
      return true;
    } catch (error) {
      console.error('Logout error:', error);
      return false;
    }
  },
  
  getUserProfile: async () => {
    return api.get('user/profile/');
  },
  
  verifyToken: async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/token/verify/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      
      return response.ok;
    } catch {
      return false;
    }
  }
};

export const backgroundsApi = {
  getBackgrounds: async (): Promise<{ backgrounds: BackgroundData[], activeBackground: BackgroundData | null }> => {
    const response = await api.get<{ backgrounds: BackgroundData[], status: string }>('backgrounds/');
    const backgrounds = response.backgrounds || [];
    const activeBackground = backgrounds.find(bg => bg.is_active) || null;
    
    return { backgrounds, activeBackground };
  },
  
  setActiveBackgroundAPI: async (backgroundId: number) => {
    return api.post(`backgrounds/${backgroundId}/set-active/`, {});
  },
  
  deleteBackgroundAPI: async (backgroundId: number) => {
    return api.delete(`backgrounds/${backgroundId}/delete/`);
  },
  
  uploadBackground: async (formData: FormData) => {
    return api.upload('backgrounds/upload/', formData);
  }
};

export const documentsApi = {
  getDocuments: async (): Promise<{ documents: Document[], activeDocument: string | null }> => {
    try {
      console.log("API: Fetching documents");
      const response = await api.get<{ documents: Document[], status: string }>('documents/');
      
      if (!response || !response.documents) {
        console.warn("API: Documents response is empty or invalid", response);
        return { documents: [], activeDocument: null };
      }
      
      const documents = response.documents || [];
      console.log(`API: Retrieved ${documents.length} documents`);
      
      // Determine active document
      let activeDocument = null;
      for (const doc of documents) {
        if (doc.is_active) {
          const sourceName = doc.source || "Unknown";
          activeDocument = sourceName.replace(/\s*-\s*Part\s*\d+$/i, "");
          break;
        }
      }
      
      return { documents, activeDocument };
    } catch (error) {
      console.error("API: Error fetching documents:", error);
      throw error; // Rethrow to allow component to handle it
    }
  },
  
  setActiveDocuments: async (documentIds: number[]) => {
    try {
      console.log("API: Setting active documents", documentIds);
      const result = await api.post('documents/set-active/', { document_ids: documentIds });
      console.log("API: Active documents set successfully");
      return result;
    } catch (error) {
      console.error("API: Error setting active documents:", error);
      throw error;
    }
  },
  
  deleteDocument: async (documentId: number) => {
    try {
      console.log("API: Deleting document", documentId);
      const result = await api.delete(`documents/${documentId}/`);
      console.log("API: Document deleted successfully");
      return result;
    } catch (error) {
      console.error("API: Error deleting document:", error);
      throw error;
    }
  },
  
  uploadDocument: async (formData: FormData) => {
    try {
      console.log("API: Uploading document");
      const result = await api.upload('documents/upload-pdf/', formData);
      console.log("API: Document uploaded successfully", result);
      return result;
    } catch (error) {
      console.error("API: Error uploading document:", error);
      throw error;
    }
  }
};

export const promptsApi = {
  getPrompt: async () => {
    try {
      const response = await fetchWithAuth('/prompts');
      if (!response.ok) throw new Error(`Failed to get prompt: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error getting prompt:', error);
      throw error;
    }
  },
  
  updatePrompt: async (promptData: any) => {
    try {
      const response = await fetchWithAuth('/prompts', {
        method: 'POST',
        body: JSON.stringify(promptData)
      });
      if (!response.ok) throw new Error(`Failed to update prompt: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error updating prompt:', error);
      throw error;
    }
  }
};

export const settingsApi = {
  getSettings: async (): Promise<Settings> => {
    return api.get('settings/');
  },
  
  updateSettings: async (settings: Partial<Settings>) => {
    return api.post('settings/update/', settings);
  }
};

export const chatApi = {
  sendMessage: async (message: string, conversationId: string | null = null) => {
    return api.post('chat/', { message, conversation_id: conversationId });
  }
};

// Default export for easier imports
export default api;