/**
 * Documents API Service - SISMOBI v3.2.0
 * Service layer for Documents API integration
 */

const API_URL = import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export interface Document {
  id: string;
  property_id?: string;
  tenant_id?: string;
  name: string;
  type: 'contract' | 'invoice' | 'receipt' | 'report' | 'other';
  file_path: string;
  file_size: number;
  mime_type: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentCreate {
  property_id?: string;
  tenant_id?: string;
  name: string;
  type: 'contract' | 'invoice' | 'receipt' | 'report' | 'other';
  file_path: string;
  file_size: number;
  mime_type: string;
  description?: string;
}

export interface DocumentUpdate {
  name?: string;
  type?: 'contract' | 'invoice' | 'receipt' | 'report' | 'other';
  description?: string;
}

class DocumentsApiService {
  private getHeaders(): Headers {
    const token = localStorage.getItem('access_token');
    return new Headers({
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    });
  }

  async getDocuments(params?: {
    page?: number;
    page_size?: number;
    property_id?: string;
    tenant_id?: string;
    doc_type?: string;
  }): Promise<{ items: Document[]; total: number; has_more: boolean }> {
    const queryParams = new URLSearchParams();
    
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.property_id) queryParams.append('property_id', params.property_id);
    if (params?.tenant_id) queryParams.append('tenant_id', params.tenant_id);
    if (params?.doc_type) queryParams.append('doc_type', params.doc_type);

    const response = await fetch(
      `${API_URL}/api/v1/documents?${queryParams.toString()}`,
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

  async getDocument(id: string): Promise<Document> {
    const response = await fetch(`${API_URL}/api/v1/documents/${id}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createDocument(document: DocumentCreate): Promise<Document> {
    const response = await fetch(`${API_URL}/api/v1/documents`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(document),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async updateDocument(id: string, updates: DocumentUpdate): Promise<Document> {
    const response = await fetch(`${API_URL}/api/v1/documents/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async deleteDocument(id: string): Promise<{ message: string; status: string }> {
    const response = await fetch(`${API_URL}/api/v1/documents/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async uploadDocument(
    file: File,
    metadata: {
      property_id?: string;
      tenant_id?: string;
      doc_type?: string;
      description?: string;
    }
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (metadata.property_id) formData.append('property_id', metadata.property_id);
    if (metadata.tenant_id) formData.append('tenant_id', metadata.tenant_id);
    if (metadata.doc_type) formData.append('doc_type', metadata.doc_type);
    if (metadata.description) formData.append('description', metadata.description);

    const token = localStorage.getItem('access_token');
    const headers = new Headers({
      'Authorization': token ? `Bearer ${token}` : '',
    });

    const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const documentsApi = new DocumentsApiService();