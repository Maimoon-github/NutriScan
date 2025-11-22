import type { BetterSwap } from '../types/api';

interface BetterSwapsListProps {
  swaps: BetterSwap[];
}

export const BetterSwapsList = ({ swaps }: BetterSwapsListProps) => {
  if (swaps.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Better Alternatives</h3>
      <div className="space-y-3">
        {swaps.map((swap, idx) => (
          <div key={idx} className="p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-900">{swap.product_name}</span>
              <span className="text-sm font-medium text-green-700">
                Score: {swap.health_score}/10
              </span>
            </div>
            <p className="text-sm text-gray-700">{swap.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
