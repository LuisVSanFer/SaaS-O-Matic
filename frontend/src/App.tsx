import React, { useState, useEffect } from 'react';
import { exchangeRateApi } from './services/api';
import CustomerSearch from './components/CustomerSearch';
import type { ExchangeRates } from './types';
import './App.css';

const App: React.FC = () => {
  const [exchangeRates, setExchangeRates] = useState<ExchangeRates>({});
  const [selectedCurrency, setSelectedCurrency] = useState('EUR');
  const [loadingRates, setLoadingRates] = useState(true);

  useEffect(() => {
    const loadRates = async () => {
      try {
        const rates = await exchangeRateApi.getRates();
        setExchangeRates(rates);
      } catch (error) {
        console.error('Error loading exchange rates:', error);
      } finally {
        setLoadingRates(false);
      }
    };
    loadRates();
  }, []);

  if (loadingRates && Object.keys(exchangeRates).length === 0) {
    return (
      <div className="app loading">
        <div className="spinner"></div>
        <p>Cargando tipos de cambio...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <CustomerSearch
        exchangeRates={exchangeRates}
        selectedCurrency={selectedCurrency}
        onCurrencyChange={setSelectedCurrency}
      />
    </div>
  );
};

export default App;