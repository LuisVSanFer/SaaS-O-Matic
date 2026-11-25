import React, { useState, useEffect, useCallback  } from 'react';
import { simulationApi, formatCurrency } from '../services/api';
import type { SimulationPreview as SimulationPreviewType, ExchangeRates } from '../types';

interface SimulationPreviewProps {
  customerId: number;
  customerCountry: string;
  exchangeRates: ExchangeRates;
  selectedCurrency: string;
  onCurrencyChange: (currency: string) => void;
  activeUsers: number;
  storageGb: number;
  apiCalls: number;
  onActiveUsersChange: (value: number) => void;
  onStorageGbChange: (value: number) => void;
  onApiCallsChange: (value: number) => void;
}

const SimulationPreviewComponent: React.FC<SimulationPreviewProps> = ({
  customerId,
  customerCountry,
  exchangeRates,
  selectedCurrency,
  onCurrencyChange,
  activeUsers,
  storageGb,
  apiCalls,
  onActiveUsersChange,
  onStorageGbChange,
  onApiCallsChange,
}) => {
  const [preview, setPreview] = useState<SimulationPreviewType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPreview = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await simulationApi.preview(customerId, activeUsers, storageGb, apiCalls);
      setPreview(data);
    } catch (err) {
      setError('Error al calcular la simulación');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [customerId, activeUsers, storageGb, apiCalls]);

  useEffect(() => {
    fetchPreview();
  }, [fetchPreview, customerId, activeUsers, storageGb, apiCalls]);

  const handleUserChange = (value: number) => {
    onActiveUsersChange(value);
  };

  return (
    <div className="simulation-preview">
      <h3>Simulador Interactivo</h3>

      <div className="controls">
        <div className="control-group">
          <label>
            Usuarios activos: <strong>{activeUsers}</strong>
          </label>
          <input
            type="range"
            min="0"
            max="200"
            value={activeUsers}
            onChange={(e) => handleUserChange(parseInt(e.target.value))}
            className="slider"
          />
          <div className="slider-labels">
            <span>0</span>
            <span>10</span>
            <span>50</span>
            <span>200</span>
          </div>
        </div>

        <div className="control-group">
          <label>
            Almacenamiento (GB): <strong>{storageGb}</strong>
          </label>
          <input
            type="range"
            min="0"
            max="1000"
            step="10"
            value={storageGb}
            onChange={(e) => onStorageGbChange(parseInt(e.target.value))}
            className="slider"
          />
        </div>

        <div className="control-group">
          <label>
            Llamadas API estimadas: <strong>{formatNumber(apiCalls)}</strong>
          </label>
          <input
            type="range"
            min="0"
            max="1000000"
            step="1000"
            value={apiCalls}
            onChange={(e) => onApiCallsChange(parseInt(e.target.value))}
            className="slider"
          />
        </div>
      </div>

      <div className="currency-selector">
        <label>Divisa: </label>
        <select
          value={selectedCurrency}
          onChange={(e) => onCurrencyChange(e.target.value)}
          className="currency-select"
        >
          {Object.keys(exchangeRates).map((currency) => (
            <option key={currency} value={currency}>
              {currency}
            </option>
          ))}
        </select>
        <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 500, padding: '4px 8px', background: '#f1f5f9', borderRadius: '4px' }}>
          Tasa: {(exchangeRates[selectedCurrency] ?? 1).toFixed(2)}
        </span>
      </div>

      {error && <div className="error">{error}</div>}

      {preview && (
        <div className="preview-results">
          <div className="result-row">
            <span>Coste base ({activeUsers} usuarios):</span>
            <strong>{formatCurrency(preview.base_amount_cents, selectedCurrency, exchangeRates)}</strong>
          </div>
          <div className="result-row">
            <span>Impuesto ({customerCountry} - {(preview.tax_rate * 100).toFixed(0)}%):</span>
            <strong>{formatCurrency(preview.tax_amount_cents, selectedCurrency, exchangeRates)}</strong>
          </div>
          <div className="result-row total">
            <span>Total mensual:</span>
            <strong>{formatCurrency(preview.total_amount_cents, selectedCurrency, exchangeRates)}</strong>
          </div>
        </div>
      )}

      {loading && <div className="loading">Calculando...</div>}
    </div>
  );
};

const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('es-ES').format(num);
};

export default SimulationPreviewComponent;