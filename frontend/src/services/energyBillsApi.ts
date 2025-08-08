/**
 * Energy Bills API Service - SISMOBI v3.2.0
 * Service layer for Energy Bills API integration
 */

const API_URL = import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export interface EnergyBill {
  id: string;
  property_id: string;
  group_id: string;
  month: number;
  year: number;
  total_amount: number;
  total_kwh: number;
  reading_date: string;
  due_date: string;
  tenant_allocations: Record<string, number>;
  created_at: string;
  updated_at: string;
}

export interface EnergyBillCreate {
  property_id: string;
  group_id: string;
  month: number;
  year: number;
  total_amount: number;
  total_kwh: number;
  reading_date: string;
  due_date: string;
  tenant_allocations?: Record<string, number>;
}

export interface EnergyBillUpdate {
  total_amount?: number;
  total_kwh?: number;
  reading_date?: string;
  due_date?: string;
  tenant_allocations?: Record<string, number>;
}

class EnergyBillsApiService {
  private getHeaders(): Headers {
    const token = localStorage.getItem('access_token');
    return new Headers({
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    });
  }

  async getEnergyBills(params?: {
    page?: number;
    page_size?: number;
    property_id?: string;
    group_id?: string;
    year?: number;
    month?: number;
  }): Promise<{ items: EnergyBill[]; total: number; has_more: boolean }> {
    const queryParams = new URLSearchParams();
    
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.property_id) queryParams.append('property_id', params.property_id);
    if (params?.group_id) queryParams.append('group_id', params.group_id);
    if (params?.year) queryParams.append('year', params.year.toString());
    if (params?.month) queryParams.append('month', params.month.toString());

    const response = await fetch(
      `${API_URL}/api/v1/energy-bills?${queryParams.toString()}`,
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

  async getEnergyBill(id: string): Promise<EnergyBill> {
    const response = await fetch(`${API_URL}/api/v1/energy-bills/${id}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createEnergyBill(bill: EnergyBillCreate): Promise<EnergyBill> {
    const response = await fetch(`${API_URL}/api/v1/energy-bills`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(bill),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async updateEnergyBill(id: string, updates: EnergyBillUpdate): Promise<EnergyBill> {
    const response = await fetch(`${API_URL}/api/v1/energy-bills/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async deleteEnergyBill(id: string): Promise<{ message: string; status: string }> {
    const response = await fetch(`${API_URL}/api/v1/energy-bills/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getGroupSummary(
    groupId: string,
    year?: number
  ): Promise<{
    group_id: string;
    total_bills: number;
    total_amount: number;
    total_kwh: number;
    average_amount: number;
    average_kwh: number;
    bills: EnergyBill[];
  }> {
    const queryParams = new URLSearchParams();
    if (year) queryParams.append('year', year.toString());

    const response = await fetch(
      `${API_URL}/api/v1/energy-bills/group/${groupId}/summary?${queryParams.toString()}`,
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
}

export const energyBillsApi = new EnergyBillsApiService();