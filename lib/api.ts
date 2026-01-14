// API Client for Masterpost.io Backend Integration

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
const API_V2_BASE_URL = process.env.NEXT_PUBLIC_API_V2_URL || 'http://localhost:8002';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  detail?: string;
}

interface UploadResponse {
  job_id: string;
  message: string;
  files_uploaded: number;
  job_status: string;
}

interface ProcessRequest {
  job_id: string;
  pipeline: 'amazon' | 'instagram' | 'ebay';
  settings?: Record<string, any>;
}

interface ProcessResponse {
  job_id: string;
  message: string;
  pipeline: string;
  status: string;
  estimated_time_minutes: number;
}

interface JobStatus {
  job_id: string;
  status: 'uploaded' | 'processing' | 'completed' | 'completed_with_errors' | 'failed' | 'cancelled';
  total_files: number;
  processed_files: number;
  failed_files: number;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  pipeline?: string;
  error_message?: string;
  successful_files?: any[];
}

interface HybridJobStatus extends JobStatus {
  user_plan: string;
  processing_method: string;
  estimated_images: number;
  has_archives: boolean;
  current_message: string;
  processing_info: {
    plan: string;
    processing_method: string;
    qwen_api_available: boolean;
    qwen_api_access: boolean;
    priority_processing: boolean;
    watermark_required: boolean;
    max_images_per_month: number;
    estimated_quality: string;
  };
}

interface UsageInfo {
  user_id: string;
  plan: string;
  plan_features: {
    plan: string;
    max_images_per_month: number;
    max_images_per_zip: number;
    qwen_api_access: boolean;
    watermark_required: boolean;
    api_access: boolean;
    priority_processing: boolean;
    price_usd: number;
    description: string;
  };
  current_usage: {
    images_processed: number;
    qwen_api_calls: number;
    usage_percentage: number;
    remaining_images: number;
  };
  limits: {
    monthly_limit: number;
    zip_limit: number;
    qwen_access: boolean;
    api_access: boolean;
  };
  billing: {
    next_billing_date?: string;
    price_usd: number;
  };
  month_year: string;
}

interface DownloadInfo {
  job_id: string;
  status: string;
  download_ready: boolean;
  files_count: number;
  total_size_mb: number;
  download_url?: string;
  expires_at?: string;
}

class ApiClient {
  private baseUrl: string;
  private v2BaseUrl: string;
  private authToken?: string;
  private userEmail?: string;

  constructor(baseUrl: string = API_BASE_URL, v2BaseUrl: string = API_V2_BASE_URL) {
    // Normalize baseUrl: remove /api/v1 or /api/v2 suffix if present
    this.baseUrl = baseUrl.replace(/\/api\/v[12]$/i, '');
    this.v2BaseUrl = v2BaseUrl.replace(/\/api\/v[12]$/i, '');
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  setUserEmail(email: string) {
    this.userEmail = email;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    useV2: boolean = false
  ): Promise<ApiResponse<T>> {
    const baseUrl = useV2 ? this.v2BaseUrl : this.baseUrl;
    // Always add /api/v1 prefix since baseUrl is normalized in constructor
    const url = `/api/v1${endpoint}`;

    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    // Add user email header for SQLite authentication
    const email = this.userEmail || (typeof window !== 'undefined' ? localStorage.getItem('mp_email') : null);
    if (email) {
      headers['x-user-email'] = email;
    }

    // Priority: 1. Class property 2. localStorage 'access_token'
    const token = this.authToken || (typeof window !== 'undefined' ? localStorage.getItem('access_token') : null);

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: AbortSignal.timeout(1800000), // 30 minutos para Qwen batch processing
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: errorData.error || `HTTP ${response.status}`,
          detail: errorData.detail || response.statusText,
        };
      }

      // Handle file downloads
      if (response.headers.get('content-type')?.includes('application/zip')) {
        const blob = await response.blob();
        return { data: blob as any };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error('API Request failed:', error);
      return {
        error: 'Network Error',
        detail: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Upload multiple images
  async uploadImages(files: File[]): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append('files', file);
    });

    return this.makeRequest<UploadResponse>('/api/v1/upload', {
      method: 'POST',
      body: formData,
    });
  }

  // Upload with progress tracking
  async uploadImagesWithProgress(
    files: File[],
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<UploadResponse>> {
    console.log('🔧 API: uploadImagesWithProgress called')
    console.log('📁 API: Number of files:', files.length)
    console.log('🌐 API: Base URL:', this.baseUrl)
    console.log('🔑 API: Auth token present:', !!this.authToken)

    return new Promise((resolve) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();

      files.forEach((file, index) => {
        console.log(`📎 API: Appending file ${index + 1} to FormData:`, {
          name: file.name,
          type: file.type,
          size: file.size
        })
        formData.append('files', file);
      });

      // Log FormData contents
      console.log('📦 API: FormData entries:')
      for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`  ${key}:`, value.name, `(${value.type}, ${value.size} bytes)`)
        } else {
          console.log(`  ${key}:`, value)
        }
      }

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const percentComplete = Math.round((e.loaded / e.total) * 100);
          console.log(`📊 API: Upload progress: ${percentComplete}% (${e.loaded}/${e.total} bytes)`)
          onProgress(percentComplete);
        }
      });

      // Handle completion
      xhr.addEventListener('load', () => {
        console.log(`📡 API: Upload completed with status: ${xhr.status}`)
        console.log('📄 API: Response text:', xhr.responseText.substring(0, 500))

        if (xhr.status === 200) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log('✅ API: Upload successful:', data)
            resolve({ data });
          } catch (error) {
            console.error('❌ API: Failed to parse response:', error)
            resolve({ error: 'Failed to parse response' });
          }
        } else {
          console.error(`❌ API: Upload failed with status ${xhr.status}`)
          try {
            const errorData = JSON.parse(xhr.responseText);
            console.error('❌ API: Error data:', errorData)
            resolve({ error: errorData.error || errorData.detail || `HTTP ${xhr.status}` });
          } catch {
            console.error('❌ API: Could not parse error response')
            resolve({ error: `HTTP ${xhr.status}: ${xhr.responseText.substring(0, 200)}` });
          }
        }
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        console.error('❌ API: Network error occurred')
        resolve({ error: 'Network Error' });
      });

      // Send request (baseUrl is already normalized without /api/v1)
      const url = "/api/v1/upload";
      console.log('🚀 API: Sending POST request to:', url)
      xhr.open('POST', url);

      // Add user email header for SQLite authentication
      const email = this.userEmail || (typeof window !== 'undefined' ? localStorage.getItem('mp_email') : null);
      if (email) {
        console.log('📧 API: Adding x-user-email header')
        xhr.setRequestHeader('x-user-email', email);
      }

      if (this.authToken) {
        console.log('🔑 API: Adding Authorization header')
        xhr.setRequestHeader('Authorization', `Bearer ${this.authToken}`);
      }

      console.log('📤 API: Sending FormData...')
      xhr.send(formData);
    });
  }

  // Start processing with selected pipeline
  async processImages(request: ProcessRequest): Promise<ApiResponse<ProcessResponse>> {
    return this.makeRequest<ProcessResponse>('/process', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get job status and progress
  async getJobStatus(jobId: string): Promise<ApiResponse<JobStatus>> {
    return this.makeRequest<JobStatus>(`/status/${jobId}`);
  }

  // Get download information
  async getDownloadInfo(jobId: string): Promise<ApiResponse<DownloadInfo>> {
    return this.makeRequest<DownloadInfo>(`/download/info/${jobId}`);
  }

  // Download processed images as ZIP
  async downloadImages(jobId: string): Promise<ApiResponse<Blob>> {
    return this.makeRequest<Blob>(`/download/${jobId}`);
  }

  // Cancel a job
  async cancelJob(jobId: string): Promise<ApiResponse<{ message: string; job_id: string }>> {
    return this.makeRequest(`/cancel/${jobId}`, {
      method: 'POST',
    });
  }

  // Get available pipelines
  async getPipelines(): Promise<ApiResponse<{ pipelines: any[] }>> {
    return this.makeRequest('/pipelines');
  }

  // Cleanup job files
  async cleanupJob(jobId: string): Promise<ApiResponse<{ message: string; job_id: string }>> {
    return this.makeRequest(`/download/${jobId}`, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; service: string }>> {
    return this.makeRequest('/health');
  }

  // === HYBRID V2 ENDPOINTS ===

  // Upload with ZIP support and plan validation
  async uploadHybrid(files: File[], userId?: string): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append('files', file);
    });

    if (userId) {
      formData.append('user_id', userId);
    }

    return this.makeRequest<UploadResponse>('/upload-hybrid', {
      method: 'POST',
      body: formData,
    }, true);
  }

  // Process with hybrid system
  async processHybrid(request: ProcessRequest): Promise<ApiResponse<ProcessResponse>> {
    return this.makeRequest<ProcessResponse>('/process-hybrid', {
      method: 'POST',
      body: JSON.stringify(request),
    }, true);
  }

  // Get hybrid job status with plan info
  async getHybridStatus(jobId: string): Promise<ApiResponse<HybridJobStatus>> {
    return this.makeRequest<HybridJobStatus>(`/status-hybrid/${jobId}`, {}, true);
  }

  // Download from hybrid system
  async downloadHybrid(jobId: string): Promise<ApiResponse<Blob>> {
    return this.makeRequest<Blob>(`/download-hybrid/${jobId}`, {}, true);
  }

  // Get user usage information
  async getUserUsage(userId: string = 'demo_user'): Promise<ApiResponse<UsageInfo>> {
    return this.makeRequest<UsageInfo>(`/usage/${userId}`, {}, true);
  }

  // Get processing info for user's plan
  async getProcessingInfo(userId: string = 'demo_user'): Promise<ApiResponse<any>> {
    return this.makeRequest(`/processing-info/${userId}`, {}, true);
  }
}

// Create a singleton instance
export const apiClient = new ApiClient();

// Utility functions for V2 hybrid processing
export class HybridProcessingApi {
  static async uploadAndProcessHybrid(
    files: File[],
    pipeline: 'amazon' | 'instagram' | 'ebay',
    settings?: Record<string, any>,
    userId?: string
  ): Promise<{ jobId?: string; error?: string; hybridInfo?: any }> {

    // Step 1: Upload files with hybrid support
    const uploadResult = await apiClient.uploadHybrid(files, userId);
    if (uploadResult.error || !uploadResult.data) {
      return { error: uploadResult.error || 'Upload failed' };
    }

    const jobId = uploadResult.data.job_id;

    // Step 2: Start hybrid processing
    const processResult = await apiClient.processHybrid({
      job_id: jobId,
      pipeline,
      settings,
    });

    if (processResult.error) {
      return { error: processResult.error };
    }

    return {
      jobId,
      hybridInfo: {
        estimatedImages: uploadResult.data.files_uploaded,
        message: uploadResult.data.message
      }
    };
  }

  static async pollHybridJobStatus(
    jobId: string,
    onProgress: (status: HybridJobStatus) => void,
    pollInterval: number = 3000
  ): Promise<HybridJobStatus> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        const result = await apiClient.getHybridStatus(jobId);

        if (result.error || !result.data) {
          reject(new Error(result.error || 'Failed to get job status'));
          return;
        }

        const status = result.data;
        onProgress(status);

        // Check if job is complete
        if (['completed', 'completed_with_errors', 'failed', 'cancelled'].includes(status.status)) {
          resolve(status);
          return;
        }

        // Continue polling
        setTimeout(poll, pollInterval);
      };

      poll();
    });
  }

  static async downloadHybridResults(jobId: string, filename?: string): Promise<void> {
    const result = await apiClient.downloadHybrid(jobId);

    if (result.error || !result.data) {
      throw new Error(result.error || 'Download failed');
    }

    // Create download link
    const blob = result.data as Blob;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `masterpost_hybrid_${jobId}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  static async getUserDashboardInfo(userId: string = 'demo_user'): Promise<{
    usage?: UsageInfo;
    processingInfo?: any;
    error?: string;
  }> {
    try {
      // Fetch both usage and processing info in parallel
      const [usageResult, processingResult] = await Promise.all([
        apiClient.getUserUsage(userId),
        apiClient.getProcessingInfo(userId)
      ]);

      if (usageResult.error) {
        return { error: usageResult.error };
      }

      return {
        usage: usageResult.data,
        processingInfo: processingResult.data
      };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  static async validateZipUpload(files: File[]): Promise<{
    valid: boolean;
    errors: string[];
    archiveCount: number;
    imageCount: number;
  }> {
    const errors: string[] = [];
    let archiveCount = 0;
    let imageCount = 0;

    const supportedImages = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'];
    const supportedArchives = ['.zip', '.rar', '.7z'];

    for (const file of files) {
      const ext = file.name.toLowerCase().split('.').pop() || '';
      const fileExtWithDot = '.' + ext;

      if (supportedArchives.includes(fileExtWithDot)) {
        archiveCount++;
        // Note: Can't validate archive contents client-side
      } else if (supportedImages.includes(fileExtWithDot)) {
        imageCount++;
      } else {
        errors.push(`Unsupported file type: ${file.name}`);
      }

      // Size check
      const maxSize = 100 * 1024 * 1024; // 100MB
      if (file.size > maxSize) {
        errors.push(`File too large: ${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      archiveCount,
      imageCount
    };
  }
}

// Utility functions for common operations (V1 compatibility)
export class ImageProcessingApi {
  static async uploadAndProcess(
    files: File[],
    pipeline: 'amazon' | 'instagram' | 'ebay',
    settings?: Record<string, any>,
    onUploadProgress?: (progress: number) => void
  ): Promise<{ jobId?: string; error?: string }> {

    // Step 1: Upload files with progress tracking
    const uploadResult = onUploadProgress
      ? await apiClient.uploadImagesWithProgress(files, onUploadProgress)
      : await apiClient.uploadImages(files);

    if (uploadResult.error || !uploadResult.data) {
      return { error: uploadResult.error || 'Upload failed' };
    }

    const jobId = uploadResult.data.job_id;

    // Step 2: Start processing
    const processResult = await apiClient.processImages({
      job_id: jobId,
      pipeline,
      settings,
    });

    if (processResult.error) {
      return { error: processResult.error };
    }

    return { jobId };
  }

  static async pollJobStatus(
    jobId: string,
    onProgress: (status: JobStatus) => void,
    pollInterval: number = 2000
  ): Promise<JobStatus> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        const result = await apiClient.getJobStatus(jobId);

        if (result.error || !result.data) {
          reject(new Error(result.error || 'Failed to get job status'));
          return;
        }

        const status = result.data;
        onProgress(status);

        // Check if job is complete
        if (['completed', 'completed_with_errors', 'failed', 'cancelled'].includes(status.status)) {
          resolve(status);
          return;
        }

        // Continue polling
        setTimeout(poll, pollInterval);
      };

      poll();
    });
  }

  static async downloadProcessedImages(jobId: string, filename?: string): Promise<void> {
    const result = await apiClient.downloadImages(jobId);

    if (result.error || !result.data) {
      throw new Error(result.error || 'Download failed');
    }

    // Ensure we have a valid Blob object
    let blob: Blob;
    if (result.data instanceof Blob) {
      blob = result.data;
    } else {
      // If data is not a Blob, convert it (fallback for non-ZIP responses)
      console.warn('Response data is not a Blob, attempting to convert');
      const dataStr = typeof result.data === 'string' ? result.data : JSON.stringify(result.data);
      blob = new Blob([dataStr], { type: 'application/octet-stream' });
    }

    // Validate blob size
    if (blob.size === 0) {
      throw new Error('Downloaded file is empty');
    }

    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `masterpost_${jobId}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Get preview URL for a specific processed image
   * @param jobId - Job ID
   * @param filename - Processed filename
   * @returns Full URL to preview image
   */
  static getPreviewUrl(jobId: string, filename: string): string {
    return `/api/v1/processed/${jobId}/${filename}`;
  }
  static async downloadSingleImage(jobId: string, filename: string): Promise<void> {
    const url = this.getPreviewUrl(jobId, filename);
    // Open in new tab instead of forcing download
    window.open(url, '_blank', 'noopener,noreferrer');
  }

  /**
   * Preload images for faster gallery display
   * @param jobId - Job ID
   * @param filenames - Array of processed filenames
   */
  static preloadImages(jobId: string, filenames: string[]): void {
    filenames.forEach((filename) => {
      const img = new Image();
      img.src = this.getPreviewUrl(jobId, filename);
    });
  }
}

// Export types for use in components
export type {
  UploadResponse,
  ProcessRequest,
  ProcessResponse,
  JobStatus,
  HybridJobStatus,
  UsageInfo,
  DownloadInfo,
  ApiResponse,
};

export default apiClient;