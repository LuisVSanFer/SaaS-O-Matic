import axios from 'axios';
import type { Customer, Simulation, CreateCustomerData, CreateSimulationData, SimulationPreview } from '../types';

const API_BASE_URL = 'http://localhost:8000';
const EXCHANGE_RATE_API = 'https://open.er-api.com/v6/latest/EUR';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const customerApi = {
  create: async (data: CreateCustomerData): Promise<Customer> => {
    const response = await api.post<Customer>('/customers', data);
    return response.data;
  },

  getAll: async (): Promise<Customer[]> => {
    const response = await api.get<Customer[]>('/customers');
    return response.data;
  },

  getById: async (id: number): Promise<Customer> => {
    const response = await api.get<Customer>(`/customers/${id}`);
    return response.data;
  },

  search: async (query: string): Promise<Customer[]> => {
    const all = await customerApi.getAll();
    const lowerQuery = query.toLowerCase();
    return all.filter(c =>
      c.company_name.toLowerCase().includes(lowerQuery) ||
      c.tax_id.toLowerCase().includes(lowerQuery)
    );
  },
};

export const simulationApi = {
  create: async (data: CreateSimulationData): Promise<Simulation> => {
    const response = await api.post<Simulation>('/simulations', data);
    return response.data;
  },

  getByCustomer: async (customerId: number): Promise<Simulation[]> => {
    const response = await api.get<Simulation[]>(`/customers/${customerId}/simulations`);
    return response.data;
  },

  getById: async (id: number): Promise<Simulation> => {
    const response = await api.get<Simulation>(`/simulations/${id}`);
    return response.data;
  },

  preview: async (customerId: number, activeUsers: number): Promise<SimulationPreview> => {
    // Get customer to know their country for tax calculation
    const customer = await customerApi.getById(customerId);
    const response = await api.post<SimulationPreview>(`/simulations/preview`, {
      customer_id: customerId,
      active_users: activeUsers,
      storage_gb: 0,
      estimated_api_calls: 0,
    });
    return response.data;
  },
};

export const exchangeRateApi = {
  getRates: async (): Promise<Record<string, number>> => {
    try {
      const response = await axios.get(EXCHANGE_RATE_API);
      if (response.data.result === 'success') {
        return response.data.rates;
      }
      throw new Error('Failed to fetch exchange rates');
    } catch (error) {
      console.error('Error fetching exchange rates:', error);
      // Return fallback rates
      return {
        EUR: 1,
        USD: 1.08,
        GBP: 0.85,
        JPY: 160,
        CHF: 0.95,
        CAD: 1.48,
        AUD: 1.65,
      };
    }
  },
};

export const formatCurrency = (amountCents: number, currency: string, exchangeRates: Record<string, number>): string => {
  const rate = exchangeRates[currency] || 1;
  const amountEuros = amountCents / 100;
  const convertedAmount = amountEuros * rate;

  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(convertedAmount);
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('es-ES').format(num);
};