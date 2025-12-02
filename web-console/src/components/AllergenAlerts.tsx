import type { AllergenAlert } from '../types/api';

interface AllergenAlertsProps {
  allergens: AllergenAlert[];
}

export const AllergenAlerts = ({ allergens }: AllergenAlertsProps) => {
  if (allergens.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <p className="text-green-800 font-medium">✓ No allergens detected</p>
      </div>
    );
  }

  const severityColors = {
    low: 'bg-yellow-100 border-yellow-300 text-yellow-800',
    medium: 'bg-orange-100 border-orange-300 text-orange-800',
    high: 'bg-red-100 border-red-300 text-red-800',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">⚠️ Allergen Alerts</h3>
      <div className="space-y-3">
        {allergens.map((alert, idx) => (
          <div key={idx} className={`border rounded-lg p-4 ${severityColors[alert.severity]}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-lg">{alert.allergen}</span>
              <span className="text-xs uppercase font-semibold">{alert.severity}</span>
            </div>
            <p className="text-sm">Source: {alert.source}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
