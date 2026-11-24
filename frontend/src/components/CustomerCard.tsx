import React, { useState, useEffect, useCallback } from 'react';
import { simulationApi, formatCurrency } from '../services/api';
import SimulationPreview from './SimulationPreview';
import type { Customer, Simulation, ExchangeRates } from '../types';

interface CustomerCardProps {
  customer: Customer;
  exchangeRates: ExchangeRates;
  selectedCurrency: string;
  onCurrencyChange: (currency: string) => void;
}

const CustomerCard: React.FC<CustomerCardProps> = ({
  customer,
  exchangeRates,
  selectedCurrency,
  onCurrencyChange,
}) => {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSimulations, setShowSimulations] = useState(false);
  const [creatingSimulation, setCreatingSimulation] = useState(false);
  const [newSimData, setNewSimData] = useState({
    active_users: 10,
    storage_gb: 100,
    estimated_api_calls: 10000,
  });

  const loadSimulations = useCallback(async () => {
    setLoading(true);
    try {
      const data = await simulationApi.getByCustomer(customer.id);
      setSimulations(data);
    } catch (error) {
      console.error('Error loading simulations:', error);
    } finally {
      setLoading(false);
    }
  }, [customer.id]);

  useEffect(() => {
    loadSimulations();
  }, [loadSimulations]);

  const handleCreateSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const simulation = await simulationApi.create({
        customer_id: customer.id,
        ...newSimData,
      });
      setSimulations(prev => [simulation, ...prev]);
      setNewSimData({ active_users: 10, storage_gb: 100, estimated_api_calls: 10000 });
      setCreatingSimulation(false);
    } catch (error) {
      console.error('Error creating simulation:', error);
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan.toLowerCase()) {
      case 'basic': return '#3b82f6';
      case 'professional': return '#8b5cf6';
      case 'enterprise': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  return (
    <div className="customer-card">
      <div className="card-header">
        <div>
          <h3>{customer.company_name}</h3>
          <span
            className="plan-badge"
            style={{ backgroundColor: getPlanColor(customer.plan) }}
          >
            {customer.plan}
          </span>
        </div>
        <button
          className="toggle-btn"
          onClick={() => setShowSimulations(!showSimulations)}
        >
          {showSimulations ? 'Ocultar' : 'Ver'} simulaciones
        </button>
      </div>

      <div className="card-details">
        <div className="detail-row">
          <span className="label">NIF/CIF:</span>
          <span className="value">{customer.tax_id}</span>
        </div>
        <div className="detail-row">
          <span className="label">Email:</span>
          <span className="value">{customer.email}</span>
        </div>
        <div className="detail-row">
          <span className="label">País:</span>
          <span className="value">{customer.country}</span>
        </div>
        <div className="detail-row">
          <span className="label">Registrado:</span>
          <span className="value">
            {new Date(customer.created_at).toLocaleDateString('es-ES')}
          </span>
        </div>
      </div>

      {/* Simulation Preview */}
      <SimulationPreview
        customerId={customer.id}
        customerCountry={customer.country}
        exchangeRates={exchangeRates}
        selectedCurrency={selectedCurrency}
        onCurrencyChange={onCurrencyChange}
      />

      {/* Simulations History */}
      {showSimulations && (
        <div className="simulations-section">
          <div className="section-header">
            <h4>Historial de Simulaciones</h4>
            <button
              className="btn btn-primary"
              onClick={() => setCreatingSimulation(!creatingSimulation)}
            >
              {creatingSimulation ? 'Cancelar' : 'Nueva Simulación'}
            </button>
          </div>

          {creatingSimulation && (
            <form onSubmit={handleCreateSimulation} className="simulation-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Usuarios activos</label>
                  <input
                    type="number"
                    min="0"
                    value={newSimData.active_users}
                    onChange={(e) => setNewSimData(prev => ({ ...prev, active_users: parseInt(e.target.value) || 0 }))}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Almacenamiento (GB)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={newSimData.storage_gb}
                    onChange={(e) => setNewSimData(prev => ({ ...prev, storage_gb: parseFloat(e.target.value) || 0 }))}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Llamadas API estimadas</label>
                  <input
                    type="number"
                    min="0"
                    value={newSimData.estimated_api_calls}
                    onChange={(e) => setNewSimData(prev => ({ ...prev, estimated_api_calls: parseInt(e.target.value) || 0 }))}
                    required
                  />
                </div>
              </div>
              <button type="submit" className="btn btn-success">Crear Simulación</button>
            </form>
          )}

          {loading ? (
            <div className="loading">Cargando simulaciones...</div>
          ) : simulations.length === 0 ? (
            <div className="empty-state">No hay simulaciones registradas</div>
          ) : (
            <div className="simulations-list">
              {simulations.map((sim) => (
                <div key={sim.id} className="simulation-item">
                  <div className="sim-info">
                    <span className="sim-users">{sim.active_users} usuarios</span>
                    <span className="sim-date">
                      {new Date(sim.created_at).toLocaleDateString('es-ES')}
                    </span>
                  </div>
                  <div className="sim-amounts">
                    <span className="sim-base">
                      Base: {formatCurrency(sim.base_amount_cents, selectedCurrency, exchangeRates)}
                    </span>
                    <span className="sim-total">
                      Total: {formatCurrency(sim.total_amount_cents, selectedCurrency, exchangeRates)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CustomerCard;