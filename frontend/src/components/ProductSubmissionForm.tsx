import React, { useState } from 'react';

const ProductSubmissionForm: React.FC = () => {
  const [deviceModel, setDeviceModel] = useState('');
  const [condition, setCondition] = useState('New');
  const [ageInMonths, setAgeInMonths] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setMessage('Submitting...');

    try {
      const response = await fetch('/api/v1/products/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_model: deviceModel,
          condition: condition,
          age_in_months: parseInt(ageInMonths),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`Product registered successfully! ID: ${data.id}, Offer Price: ${data.initial_offer_price}`);
        setDeviceModel('');
        setAgeInMonths('');
      } else {
        const errorData = await response.json();
        setMessage(`Error: ${errorData.detail || 'Something went wrong.'}`);
      }
    } catch (error) {
      setMessage(`Network error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '500px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h2 style={{ textAlign: 'center', color: '#333' }}>Register New Product</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label htmlFor="deviceModel" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Device Model:</label>
          <input
            type="text"
            id="deviceModel"
            value={deviceModel}
            onChange={(e) => setDeviceModel(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          />
        </div>

        <div>
          <label htmlFor="condition" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Condition:</label>
          <select
            id="condition"
            value={condition}
            onChange={(e) => setCondition(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          >
            <option value="New">New</option>
            <option value="Used - Like New">Used - Like New</option>
            <option value="Used - Good">Used - Good</option>
            <option value="Used - Fair">Used - Fair</option>
          </select>
        </div>

        <div>
          <label htmlFor="ageInMonths" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Age in Months:</label>
          <input
            type="number"
            id="ageInMonths"
            value={ageInMonths}
            onChange={(e) => setAgeInMonths(e.target.value)}
            required
            min="0"
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          />
        </div>

        <button
          type="submit"
          style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }}
        >
          Register Product
        </button>
      </form>
      {message && <p style={{ marginTop: '20px', padding: '10px', backgroundColor: '#e9ecef', borderRadius: '4px' }}>{message}</p>}
    </div>
  );
};

export default ProductSubmissionForm;
