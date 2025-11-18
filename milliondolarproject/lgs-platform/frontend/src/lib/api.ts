import axios, { AxiosInstance } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/auth/login";
    }
    return Promise.reject(error);
  }
);

// Enhanced API client with all our improvements
class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL;
  }

  private getAuthHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return response.json();
  }

  // Authentication
  async login(email: string, password: string): Promise<{ access_token: string }> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
    });

    if (!response.ok) {
      throw new Error(`Login failed: ${response.status}`);
    }

    return response.json();
  }

  // Student APIs
  async getStudentDashboard(): Promise<any> {
    return this.request('/api/v1/student/dashboard');
  }

  async getStudentProfile(): Promise<any> {
    return this.request('/api/v1/student/profile');
  }

  async getStudentPerformanceAnalytics(): Promise<any> {
    return this.request('/api/v1/student/performance/analytics');
  }

  async getStudentRecommendations(): Promise<any> {
    return this.request('/api/v1/student/recommendations');
  }

  async getExamBundles(): Promise<any> {
    return this.request('/api/v1/exams/bundles');
  }

  async createExamSession(bundleId: string): Promise<any> {
    return this.request(`/api/v1/exams/bundles/${bundleId}/sessions`, {
      method: 'POST',
    });
  }

  async submitAnswer(sessionId: string, answerData: any): Promise<any> {
    return this.request(`/api/v1/exams/sessions/${sessionId}/submit`, {
      method: 'POST',
      body: JSON.stringify(answerData),
    });
  }

  // Teacher APIs
  async getTeacherDashboardSummary(): Promise<any> {
    return this.request('/api/v1/teachers/dashboard-summary');
  }

  async getClassOverview(classId: string): Promise<any> {
    return this.request(`/api/v1/teachers/classes/${classId}/overview`);
  }

  async getStudentProfileForTeacher(studentId: string): Promise<any> {
    return this.request(`/api/v1/teachers/students/${studentId}/profile`);
  }

  async getLearningOutcomeAnalysis(learningOutcome: string, subject: string): Promise<any> {
    return this.request(`/api/v1/teachers/learning-outcomes/${encodeURIComponent(learningOutcome)}/analysis?subject=${encodeURIComponent(subject)}`);
  }

  async getVideoRecommendations(studentId: string, limit: number = 5): Promise<any> {
    return this.request(`/api/v1/teachers/students/${studentId}/video-recommendations?limit=${limit}`);
  }

  async assignVideoToStudent(videoId: string, studentId: string): Promise<any> {
    return this.request(`/api/v1/teachers/videos/${videoId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId }),
    });
  }

  async generateMiniTest(testData: any): Promise<any> {
    return this.request('/api/v1/teachers/mini-tests/generate', {
      method: 'POST',
      body: JSON.stringify(testData),
    });
  }

  async getActiveAlerts(classId?: string, severity?: string): Promise<any> {
    const params = new URLSearchParams();
    if (classId) params.append('class_id', classId);
    if (severity) params.append('severity', severity);
    
    return this.request(`/api/v1/teachers/alerts${params.toString() ? '?' + params.toString() : ''}`);
  }

  async resolveAlert(alertId: string, resolutionNote: string): Promise<any> {
    return this.request(`/api/v1/teachers/alerts/${alertId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution_note: resolutionNote }),
    });
  }

  async getClassPerformanceTrends(classId: string, days: number = 30, subject?: string): Promise<any> {
    const params = new URLSearchParams({ days: days.toString() });
    if (subject) params.append('subject', subject);
    
    return this.request(`/api/v1/teachers/classes/${classId}/performance-trends?${params.toString()}`);
  }

  async registerTeacherAccess(accessData: any): Promise<any> {
    return this.request('/api/v1/teachers/register-access', {
      method: 'POST',
      body: JSON.stringify(accessData),
    });
  }

  async recordStudentSubmission(classId: string, submissionData: any): Promise<any> {
    return this.request(`/api/v1/teachers/classes/${classId}/submissions`, {
      method: 'POST',
      body: JSON.stringify(submissionData),
    });
  }

  // Enhanced Question Generation APIs
  async generateQuestions(criteria: any): Promise<any> {
    return this.request('/api/v1/generation/generate', {
      method: 'POST',
      body: JSON.stringify(criteria),
    });
  }

  async generateQuestionsWithDifficulty(criteria: any): Promise<any> {
    return this.request('/api/v1/generation/generate-with-difficulty', {
      method: 'POST',
      body: JSON.stringify(criteria),
    });
  }

  async generateAdaptiveQuestions(studentId: string, criteria: any): Promise<any> {
    return this.request('/api/v1/generation/adaptive', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId, ...criteria }),
    });
  }

  async batchGenerateQuestions(requests: any[]): Promise<any> {
    return this.request('/api/v1/generation/batch', {
      method: 'POST',
      body: JSON.stringify({ generation_requests: requests }),
    });
  }

  async getGenerationHistory(): Promise<any> {
    return this.request('/api/v1/generation/history');
  }

  async getGenerationMetrics(): Promise<any> {
    return this.request('/api/v1/generation/metrics');
  }

  async getCacheStatus(): Promise<any> {
    return this.request('/api/v1/generation/cache/status');
  }

  async preGenerateQuestions(criteria: any): Promise<any> {
    return this.request('/api/v1/generation/cache/pre-generate', {
      method: 'POST',
      body: JSON.stringify(criteria),
    });
  }

  // Admin APIs - Placeholder for future implementation
  async getSystemStats(): Promise<any> {
    return { totalUsers: 0, totalSchools: 0, systemHealth: 'Operational', pendingReviews: 0 };
  }

  async getSystemHealth(): Promise<any> {
    return { status: 'healthy', uptime: '99.9%' };
  }

  async getSystemLogs(limit: number = 100): Promise<any> {
    // TODO: Implement system logs fetching
    return { logs: [], limit };
  }

  async getQuestionBankStats(): Promise<any> {
    return { totalQuestions: 0, totalSubjects: 0 };
  }

  async getPerformanceMetrics(): Promise<any> {
    return { averageResponseTime: 0, successRate: 100 };
  }

  async getUserManagement(): Promise<any> {
    return { users: [] };
  }

  async createUser(userData: any): Promise<any> {
    // TODO: Implement user creation
    console.log('Creating user:', userData);
    return { success: true, userId: 'new-user-id' };
  }

  async updateUser(userId: string, userData: any): Promise<any> {
    // TODO: Implement user update
    console.log('Updating user:', userId, userData);
    return { success: true };
  }

  async deleteUser(userId: string): Promise<any> {
    // TODO: Implement user deletion
    console.log('Deleting user:', userId);
    return { success: true };
  }

  async bulkImportQuestions(file: File): Promise<any> {
    // TODO: Implement bulk question import
    console.log('Importing questions from file:', file.name);
    return { success: true, imported: 0 };
  }

  // General APIs
  async getHealth(): Promise<any> {
    return this.request('/health');
  }

  async getTopics(): Promise<any> {
    return this.request('/api/v1/curriculum/topics');
  }

  async getSubjects(): Promise<any> {
    return this.request('/api/v1/curriculum/subjects');
  }

  async getLearningOutcomes(): Promise<any> {
    return this.request('/api/v1/curriculum/learning-outcomes');
  }
}

export const enhancedApiClient = new APIClient();
export default apiClient;
