/**
 * Reports API Service - SISMOBI v3.2.0
 * Service layer for Reports API integration
 */

const API_URL = import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export interface ReportFilters {
  properties: Array<{
    id: string;
    address: string;
    type: string;
    status: string;
  }>;
  tenants: Array<{
    id: string;
    name: string;
    email: string;
    status: string;
  }>;
  property_status: string[];
  tenant_status: string[];
  property_types: string[];
  quick_periods: Array<{
    key: string;
    label: string;
  }>;
}

class ReportsApiService {
  private getHeaders(): Headers {
    const token = localStorage.getItem('access_token');
    return new Headers({
      'Authorization': token ? `Bearer ${token}` : '',
    });
  }

  async generateFinancialReport(params?: {
    start_date?: string;
    end_date?: string;
    property_id?: string;
    tenant_id?: string;
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    if (params?.property_id) queryParams.append('property_id', params.property_id);
    if (params?.tenant_id) queryParams.append('tenant_id', params.tenant_id);

    const response = await fetch(
      `${API_URL}/api/v1/reports/financial?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.blob();
  }

  async generatePropertiesReport(params?: {
    status?: string;
    property_type?: string;
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    
    if (params?.status) queryParams.append('status', params.status);
    if (params?.property_type) queryParams.append('property_type', params.property_type);

    const response = await fetch(
      `${API_URL}/api/v1/reports/properties?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.blob();
  }

  async generateTenantsReport(params?: {
    property_id?: string;
    status?: string;
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    
    if (params?.property_id) queryParams.append('property_id', params.property_id);
    if (params?.status) queryParams.append('status', params.status);

    const response = await fetch(
      `${API_URL}/api/v1/reports/tenants?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.blob();
  }

  async generateComprehensiveReport(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const response = await fetch(
      `${API_URL}/api/v1/reports/comprehensive?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.blob();
  }

  async generateQuickFinancialReport(period: string): Promise<Blob> {
    const queryParams = new URLSearchParams();
    queryParams.append('period', period);

    const response = await fetch(
      `${API_URL}/api/v1/reports/quick-financial?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.blob();
  }

  async getAvailableFilters(): Promise<ReportFilters> {
    const response = await fetch(
      `${API_URL}/api/v1/reports/available-filters`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getReportsHistory(limit: number = 20): Promise<{
    message: string;
    reports: any[];
    total: number;
    note: string;
  }> {
    const queryParams = new URLSearchParams();
    queryParams.append('limit', limit.toString());

    const response = await fetch(
      `${API_URL}/api/v1/reports/history?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Helper method to download blob as file
   */
  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

export const reportsApi = new ReportsApiService();