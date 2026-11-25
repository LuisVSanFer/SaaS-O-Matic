import React, { useState, useEffect, useCallback } from 'react';
import { simulationApi, customerApi, formatCurrency } from '../services/api';
import type { Customer, Simulation, ExchangeRates } from '../types';
import SimulationPreview from './SimulationPreview';
import { useToast } from '../hooks/useToast';

interface CustomerCardProps {
  customer: Customer;
  exchangeRates?: ExchangeRates;
  selectedCurrency?: string;
  onCurrencyChange?: (c: string) => void;
  onDelete?: (customerId: number) => void;
}

const CustomerCard: React.FC<CustomerCardProps> = ({
  customer,
  exchangeRates = { EUR: 1, USD: 1.08, GBP: 0.86 },
  selectedCurrency = 'EUR',
  onCurrencyChange = () => {},
  onDelete
}) => {
  const { showToast } = useToast();
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSimulations, setShowSimulations] = useState(false);

  // ESTADO UNIFICADO CON LOS 3 CAMPOS
  const [simData, setSimData] = useState({
    active_users: 1,
    storage_gb: 0,
    estimated_api_calls: 0,
  });

  const loadSimulations = useCallback(async () => {
    setLoading(true);
    try {
      const data = await simulationApi.getByCustomer(customer.id);
      setSimulations(data);
    } catch (error) {
      console.error('Error cargando simulaciones:', error);
    } finally {
      setLoading(false);
    }
  }, [customer.id]);

  useEffect(() => {
    if (showSimulations) loadSimulations();
  }, [showSimulations, loadSimulations]);


  const handleCreateSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await simulationApi.create({
        customer_id: customer.id,
        ...simData,
      });
      setSimData({ active_users: 1, storage_gb: 0, estimated_api_calls: 0 });
      loadSimulations();
    } catch (error) {
      showToast('Error al crear la simulación', 'error');
    }
  };

  const handleChange = (field: keyof typeof simData, value: string | number) => {
    const numValue = typeof value === 'string' ? parseFloat(value) || 0 : value;
    setSimData(prev => ({ ...prev, [field]: numValue }));
  };

  const handleDeleteSimulation = async (simulationId: number) => {
    if (!window.confirm('¿Eliminar esta simulación?')) return;
    try {
      await simulationApi.delete(simulationId);
      setSimulations(prev => prev.filter(s => s.id !== simulationId));
      showToast('Simulación eliminada', 'success');
    } catch (err) {
      showToast('Error al eliminar simulación', 'error');
    }
  };

  const handleDeleteCustomer = async () => {
    if (!window.confirm(`¿Eliminar cliente "${customer.company_name}" y TODAS sus simulaciones?`)) return;

    try {
      await customerApi.delete(customer.id);
      showToast('Cliente eliminado', 'success');
      if (onDelete) onDelete(customer.id);
    } catch (err) {
      showToast('Error al eliminar cliente', 'error');
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '15px', margin: '10px 0', borderRadius: '8px', background: '#fff' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h3 style={{ margin: 0 }}>{customer.company_name}</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={handleDeleteCustomer}
            style={{ padding: '6px 10px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            🗑️ Eliminar
          </button>
          <button onClick={() => setShowSimulations(!showSimulations)}>
            {showSimulations ? 'Ocultar Simulaciones' : 'Ver / Crear Simulaciones'}
          </button>
        </div>
      </div>

      <p><strong>NIF/CIF:</strong> {customer.tax_id} | <strong>País:</strong> {customer.country} | <strong>Plan:</strong> {customer.plan}</p>
      <p><strong>Email:</strong> {customer.email}</p>

      {showSimulations && (
        <div style={{ marginTop: '10px', borderTop: '1px dashed #ccc', paddingTop: '10px' }}>
          <h4>Simulaciones</h4>

          <form onSubmit={handleCreateSimulation} style={{ marginBottom: '15px' }}>
            <div style={{ display: 'grid', gap: '10px', marginBottom: '10px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ minWidth: '160px' }}>Usuarios activos:</span>
                <input
                  type="number"
                  min="1"
                  value={simData.active_users}
                  onChange={(e) => handleChange('active_users', e.target.value)}
                  style={{ width: '80px' }}
                />
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ minWidth: '160px' }}>Almacenamiento (GB):</span>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={simData.storage_gb}
                  onChange={(e) => handleChange('storage_gb', e.target.value)}
                  style={{ width: '80px' }}
                />
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ minWidth: '160px' }}>Llamadas API estimadas:</span>
                <input
                  type="number"
                  min="0"
                  value={simData.estimated_api_calls}
                  onChange={(e) => handleChange('estimated_api_calls', e.target.value)}
                  style={{ width: '100px' }}
                />
              </label>
            </div>

            <SimulationPreview
              customerId={customer.id}
              customerCountry={customer.country}
              exchangeRates={exchangeRates}
              selectedCurrency={selectedCurrency}
              onCurrencyChange={onCurrencyChange}
              activeUsers={simData.active_users}
              storageGb={simData.storage_gb}
              apiCalls={simData.estimated_api_calls}
              onActiveUsersChange={(v) => handleChange('active_users', v)}
              onStorageGbChange={(v) => handleChange('storage_gb', v)}
              onApiCallsChange={(v) => handleChange('estimated_api_calls', v)}
            />  

            <button type="submit" style={{ padding: '8px 16px', background: '#10b981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Simular y Guardar
            </button>
          </form>

          {loading ? (
            <p>Cargando...</p>
          ) : simulations.length === 0 ? (
            <p style={{ color: '#666' }}>No hay simulaciones registradas para este cliente.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {simulations.map((sim) => (
                <li key={sim.id} style={{ marginBottom: '8px', padding: '8px', background: '#f9fafb', borderRadius: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div><strong>{sim.active_users} usuarios</strong> | {sim.storage_gb} GB | {sim.estimated_api_calls.toLocaleString()} API calls</div>
                    <div style={{ fontSize: '13px', color: '#374151' }}>
                      Base: <strong>{formatCurrency(sim.base_amount_cents, selectedCurrency, exchangeRates)}</strong> +
                      IVA ({(sim.tax_rate * 100)}%): <strong>{formatCurrency(sim.tax_amount_cents, selectedCurrency, exchangeRates)}</strong> =
                      Total: <strong style={{ color: 'green' }}>{formatCurrency(sim.total_amount_cents, selectedCurrency, exchangeRates)}</strong>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteSimulation(sim.id)}
                    style={{ padding: '4px 8px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: '3px', cursor: 'pointer', fontSize: '12px' }}
                  >
                    🗑️
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default CustomerCard;