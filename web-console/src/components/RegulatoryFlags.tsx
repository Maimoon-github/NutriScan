import type { RegulatoryFlag } from '../types/api';

interface RegulatoryFlagsProps {
  flags: RegulatoryFlag[];
}

export const RegulatoryFlags = ({ flags }: RegulatoryFlagsProps) => {
  if (!flags || flags.length === 0) return null;

  const severityColors: Record<string, string> = {
    low: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    medium: 'bg-orange-50 border-orange-200 text-orange-900',
    high: 'bg-red-50 border-red-200 text-red-900',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Regulatory Flags</h3>
      <div className="space-y-2">
        {flags.map((f, idx) => (
          <div key={idx} className={`border rounded p-3 ${severityColors[f.severity]}`}>
            <div className="flex justify-between">
              <span className="font-medium">{f.label}</span>
              <span className="text-xs uppercase">{f.severity}</span>
            </div>
            <p className="text-sm">Jurisdiction: {f.jurisdiction}</p>
          </div>
        ))}
      </div>
    </div>
  );
};