import type { AllergenAlert } from '../types/api';

interface AllergenChipsProps {
  alerts: AllergenAlert[];
}

export const AllergenChips = ({ alerts }: AllergenChipsProps) => {
  if (alerts.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <p className="text-green-800 font-medium">✓ No allergens detected</p>
      </div>
    );
  }

  const severityColors: Record<string, string> = {
    low: 'bg-yellow-100 text-yellow-800',
    medium: 'bg-orange-100 text-orange-800',
    high: 'bg-red-100 text-red-800',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Allergen Alerts</h3>
      <div className="flex flex-wrap gap-2">
        {alerts.map((a, idx) => (
          <div
            key={idx}
            className={`px-3 py-1 rounded-full text-sm border ${severityColors[a.severity]} border-current`}
            title={`Source: ${a.source}`}
          >
            {a.name} • {a.severity}
          </div>
        ))}
      </div>
    </div>
  );
};