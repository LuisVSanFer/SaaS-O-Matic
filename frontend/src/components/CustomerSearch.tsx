import React, { useState, useEffect } from 'react';
import { customerApi } from '../services/api';
import CustomerCard from './CustomerCard';
import type { Customer, ExchangeRates } from '../types';
import { useToast } from '../hooks/useToast';
import { Toast } from './Toast';

interface CustomerSearchProps {
  exchangeRates: ExchangeRates;
  selectedCurrency: string;
  onCurrencyChange: (currency: string) => void;
}

const CustomerSearch: React.FC<CustomerSearchProps> = ({
  exchangeRates,
  selectedCurrency,
  onCurrencyChange,
}) => {
  const { toasts, showToast, dismissToast } = useToast();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCustomer, setNewCustomer] = useState({
    company_name: '',
    tax_id: '',
    email: '',
    country: 'ES',
    plan: 'Professional',
  });

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await customerApi.getAll();
      setCustomers(data);
      setFilteredCustomers(data);
    } catch (err) {
      setError('Error al cargar clientes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setFilteredCustomers(customers);
    } else {
      const lowerQuery = query.toLowerCase();
      setFilteredCustomers(customers.filter(c =>
        c.company_name.toLowerCase().includes(lowerQuery) ||
        c.tax_id.toLowerCase().includes(lowerQuery)
      ));
    }
  };

  const handleCreateCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await customerApi.create(newCustomer);
      setShowCreateForm(false);
      setNewCustomer({ company_name: '', tax_id: '', email: '', country: 'ES', plan: 'Professional' });
      loadCustomers();
    } catch (err) {
      console.error('Error creating customer:', err);
      showToast('Error al crear cliente. Verifique que el NIF/CIF sea válido y no exista ya.', 'error');
    };
  };

  const countries = [
    { code: 'ES', name: 'España' },
    { code: 'DE', name: 'Alemania' },
    { code: 'FR', name: 'Francia' },
    { code: 'IT', name: 'Italia' },
    { code: 'PT', name: 'Portugal' },
    { code: 'NL', name: 'Países Bajos' },
    { code: 'BE', name: 'Bélgica' },
    { code: 'AT', name: 'Austria' },
    { code: 'IE', name: 'Irlanda' },
    { code: 'US', name: 'Estados Unidos' },
    { code: 'GB', name: 'Reino Unido' },
  ];

  const plans = ['Basic', 'Professional', 'Enterprise'];

  return (
    <div className="customer-search">
      <div className="search-header">
        <h2>Dashboard Comercial - SaaS-O-Matic</h2>
        <div className="header-actions">
          <select
            value={selectedCurrency}
            onChange={(e) => onCurrencyChange(e.target.value)}
            className="currency-select"
            aria-label="Seleccionar divisa"
          >
            {Object.keys(exchangeRates).map((currency) => (
              <option key={currency} value={currency}>{currency}</option>
            ))}
          </select>
          <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 500, padding: '4px 8px', background: '#f1f5f9', borderRadius: '4px' }}>
            Tasa: {(exchangeRates[selectedCurrency] ?? 1).toFixed(2)}
          </span>
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancelar' : 'Nuevo Cliente'}
          </button>
        </div>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreateCustomer} className="create-customer-form">
          <h3>Crear Nuevo Cliente</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Nombre de empresa *</label>
              <input
                type="text"
                value={newCustomer.company_name}
                onChange={(e) => setNewCustomer(prev => ({ ...prev, company_name: e.target.value }))}
                required
                placeholder="Ej: Acme Corp"
              />
            </div>
            <div className="form-group">
              <label>Identificador Fiscal (NIF/CIF) *</label>
              <input
                type="text"
                value={newCustomer.tax_id}
                onChange={(e) => setNewCustomer(prev => ({ ...prev, tax_id: e.target.value.toUpperCase() }))}
                required
                placeholder="Ej: B87654321 o 12345678Z"
                style={{ textTransform: 'uppercase' }}
              />
            </div>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                value={newCustomer.email}
                onChange={(e) => setNewCustomer(prev => ({ ...prev, email: e.target.value }))}
                required
                placeholder="contacto@empresa.com"
              />
            </div>
            <div className="form-group">
              <label>País *</label>
              <select
                value={newCustomer.country}
                onChange={(e) => setNewCustomer(prev => ({ ...prev, country: e.target.value }))}
                required
              >
                {countries.map(c => (
                  <option key={c.code} value={c.code}>{c.name} ({c.code})</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Plan *</label>
              <select
                value={newCustomer.plan}
                onChange={(e) => setNewCustomer(prev => ({ ...prev, plan: e.target.value }))}
                required
              >
                {plans.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-success">Crear Cliente</button>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreateForm(false)}>Cancelar</button>
          </div>
        </form>
      )}

      <div className="search-bar">
        <input
          type="text"
          placeholder="Buscar por nombre de empresa o NIF/CIF..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          className="search-input"
        />
        <span className="search-results">{filteredCustomers.length} cliente(s) encontrado(s)</span>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Cargando clientes...</div>
      ) : filteredCustomers.length === 0 ? (
        <div className="empty-state">
          {searchQuery ? 'No se encontraron clientes con ese criterio' : 'No hay clientes registrados. Cree su primer cliente.'}
        </div>
      ) : (
        <div className="customers-grid">
          {filteredCustomers.map((customer) => (
            <CustomerCard
              key={customer.id}
              customer={customer}
              exchangeRates={exchangeRates}
              selectedCurrency={selectedCurrency}
              onCurrencyChange={onCurrencyChange}
              onDelete={loadCustomers}
            />
          ))}
        </div>
      )}
      {toasts.map(t => (
        <Toast key={t.id} message={t.message} type={t.type} onClose={() => dismissToast(t.id)} />
      ))}
    </div>
  );
};

export default CustomerSearch;