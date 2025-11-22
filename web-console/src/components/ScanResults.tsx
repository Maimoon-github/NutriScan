import type { ScanResponse } from '../types/api';
import { TrafficLightBadge } from './TrafficLightBadge';
import { IngredientList } from './IngredientList';
import { AllergenAlerts } from './AllergenAlerts';
import { WhyAccordion } from './WhyAccordion';
import { BetterSwapsList } from './BetterSwapsList';

interface ScanResultsProps {
  result: ScanResponse;
  onReset: () => void;
}

export const ScanResults = ({ result, onReset }: ScanResultsProps) => {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scan Results</h1>
          <p className="text-sm text-gray-600 mt-1">
            Scan ID: {result.scan_id} • {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          New Scan
        </button>
      </div>

      <TrafficLightBadge trafficLight={result.traffic_light} />

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Health Impact Summary</h3>
        <p className="text-gray-700 mb-2">{result.health_impact_summary.short_summary}</p>
        <p className="text-sm text-gray-600">{result.health_impact_summary.detailed_analysis}</p>
        
        <div className="mt-4 flex gap-4 flex-wrap">
          {result.health_impact_summary.is_halal !== null && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${result.health_impact_summary.is_halal ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
              {result.health_impact_summary.is_halal ? '✓ Halal' : '✗ Not Halal'}
            </span>
          )}
          {result.health_impact_summary.is_vegan !== null && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${result.health_impact_summary.is_vegan ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
              {result.health_impact_summary.is_vegan ? '✓ Vegan' : '✗ Not Vegan'}
            </span>
          )}
          {result.health_impact_summary.is_infant_safe !== null && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${result.health_impact_summary.is_infant_safe ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {result.health_impact_summary.is_infant_safe ? '✓ Infant Safe' : '⚠ Not for Infants'}
            </span>
          )}
        </div>
      </div>

      <AllergenAlerts allergens={result.allergen_alerts} />

      <WhyAccordion why={result.why} citations={result.citations} />

      {result.parsed_ingredients.length > 0 && (
        <IngredientList ingredients={result.parsed_ingredients} />
      )}

      <BetterSwapsList swaps={result.better_swaps} />

      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <div className="flex justify-between">
          <span>OCR Confidence: {result.ocr_confidence ? `${(result.ocr_confidence * 100).toFixed(1)}%` : 'N/A'}</span>
          <span>Processing Time: {result.latency_ms}ms</span>
          <span>Status: {result.status}</span>
        </div>
      </div>
    </div>
  );
};
