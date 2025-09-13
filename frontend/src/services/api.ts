const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface Prompt {
  id: string;
  name: string;
  description: string;
}

export interface ParseResponse {
  success: boolean;
  data: {
    markdown: string;
    rawText: string;
  };
  metadata: {
    storage_key: string;
    model: string;
    processing_time_ms: number;
    request_id: string;
    file_size_kb: number;
  };
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
  };
}

class ApiService {
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      if (response.status === 422) {
        const error = await response.json();
        throw new Error(`Validation Error: ${error.detail?.[0]?.msg || 'Invalid input'}`);
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async getPrompts(): Promise<Prompt[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/prompts/`);
    const data = await this.handleResponse<{ prompts: Prompt[] }>(response);
    return data.prompts;
  }

  async parseDocument(file: File, promptId: string): Promise<ParseResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('promptId', promptId);

    const response = await fetch(`${API_BASE_URL}/api/v1/parse/`, {
      method: 'POST',
      body: formData,
    });

    return this.handleResponse<ParseResponse>(response);
  }

  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/`);
    return this.handleResponse<{ status: string; message: string }>(response);
  }
}

export const apiService = new ApiService();