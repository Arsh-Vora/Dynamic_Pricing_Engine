import React, { useState } from 'react';

interface PriceOfferDisplayProps {
  offer: { price: number; productId: number; };
}

const PriceOfferDisplay: React.FC<PriceOfferDisplayProps> = ({ offer }) => {
  const [decisionMade, setDecisionMade] = useState<'accepted' | 'declined' | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDecision = async (decision: 'accept' | 'decline') => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/v1/products/${offer.productId}/${decision}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setDecisionMade(decision === 'accept' ? 'accepted' : 'declined');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || `Failed to ${decision} offer.`);
      }
    } catch (err) {
      setError(`Network error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (decisionMade === 'accepted') {
    return (
      <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '500px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', textAlign: 'center' }}>
        <h2>Thank you for your acceptance!</h2>
        <p>We will email you with the next steps for shipping your device.</p>
      </div>
    );
  }

  if (decisionMade === 'declined') {
    return (
      <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '500px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', textAlign: 'center' }}>
        <h2>Thank you for considering us.</h2>
        <p>Your transaction has been closed.</p>
      </div>
    );
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '500px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', textAlign: 'center' }}>
      <h2>Offer Generated!</h2>
      <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>${offer.price.toFixed(2)}</p>
      {error && <p style={{ color: '#dc3545' }}>Error: {error}</p>}
      <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '20px' }}>
        <button
          onClick={() => handleDecision('accept')}
          disabled={isLoading}
          style={{ padding: '10px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }}
        >
          {isLoading && decisionMade === null ? 'Accepting...' : 'Yes, I Accept'}
        </button>
        <button
          onClick={() => handleDecision('decline')}
          disabled={isLoading}
          style={{ padding: '10px 15px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }}
        >
          {isLoading && decisionMade === null ? 'Declining...' : 'No, Thank You'}
        </button>
      </div>
    </div>
  );
};

export default PriceOfferDisplay;
