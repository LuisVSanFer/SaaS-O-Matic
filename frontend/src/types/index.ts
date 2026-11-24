export interface Customer {
  id: number;
  company_name: string;
  tax_id: string;
  email: string;
  country: string;
  plan: string;
  created_at: string;
}

export interface Simulation {
  id: number;
  customer_id: number;
  active_users: number;
  storage_gb: number;
  estimated_api_calls: number;
  base_amount_cents: number;
  tax_rate: number;
  tax_amount_cents: number;
  total_amount_cents: number;
  created_at: string;
}

export interface SimulationPreview {
  active_users: number;
  storage_gb: number;
  estimated_api_calls: number;
  base_amount_cents: number;
  tax_rate: number;
  tax_amount_cents: number;
  total_amount_cents: number;
  currency: string;
  exchange_rate: number;
}

export interface ExchangeRates {
  [currency: string]: number;
}

export interface CreateCustomerData {
  company_name: string;
  tax_id: string;
  email: string;
  country: string;
  plan: string;
}

export interface CreateSimulationData {
  customer_id: number;
  active_users: number;
  storage_gb: number;
  estimated_api_calls: number;
}