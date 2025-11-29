import type { ScanResponse } from '../types/api';
import { TrafficLightBadge } from './TrafficLightBadge';
import { IngredientList } from './IngredientList';
import { AllergenChips } from './AllergenChips';
import { WhyAccordion } from './WhyAccordion';
import { BetterSwapsList } from './BetterSwapsList';
import { RegulatoryFlags } from './RegulatoryFlags';
import { MetaPanel } from './MetaPanel';

type ApiError = {
  error: 'validation_error' | 'pipeline_error' | string;
  details?: Record<string, unknown>;
  message?: string;
};

interface ScanResultsProps {
  result: ScanResponse | ApiError;
  onReset: () => void;
}

export const ScanResults = ({ result, onReset }: ScanResultsProps) => {
  // Error handling per contract
  if ('error' in result) {
    return (
      <div className="max-w-3xl mx-auto p-6 space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Scan Error</h1>
          <button
            onClick={onReset}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>

        {result.error === 'validation_error' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="text-yellow-900 font-semibold mb-2">Invalid Upload</h3>
            <pre className="text-sm text-yellow-800 overflow-auto">{JSON.stringify(result.details ?? {}, null, 2)}</pre>
          </div>
        )}

        {result.error === 'pipeline_error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-red-900 font-semibold mb-2">Server Error</h3>
            <p className="text-sm text-red-800">{result.message ?? 'Unexpected processing error.'}</p>
          </div>
        )}
      </div>
    );
  }

  if (result.status === 'unreadable') {
    return (
      <div className="max-w-3xl mx-auto p-6 space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Scan Failed</h1>
          <button
            onClick={onReset}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retake Photo
          </button>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 space-y-2">
          <p className="text-yellow-900 font-medium">We couldn’t read the label.</p>
          <ul className="list-disc list-inside text-sm text-yellow-800">
            <li>Ensure good lighting and avoid glare.</li>
            <li>Fill the frame with the ingredient list.</li>
            <li>Hold steady and avoid motion blur.</li>
          </ul>
        </div>
        <MetaPanel ocrConfidence={result.ocr_confidence} latencyMs={result.latency_ms} status={result.status} />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scan Results</h1>
          <p className="text-sm text-gray-700 mt-1">
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

      <TrafficLightBadge trafficLight={result.traffic_light} status={result.status} />

      {result.status === 'partial_ocr_failure' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-900 font-medium">Partial OCR failure: some text may be missing or inaccurate.</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Summary</h3>
        <p className="text-gray-800">{result.summary}</p>
      </div>

      <AllergenChips alerts={result.allergen_alerts} />

      <WhyAccordion why={result.why} citations={result.citations} />

      {result.parsed_ingredients.length > 0 && (
        <IngredientList ingredients={result.parsed_ingredients} />
      )}

      <BetterSwapsList swaps={result.better_swaps} />

      <RegulatoryFlags flags={result.regulatory_flags} />

      <MetaPanel ocrConfidence={result.ocr_confidence} latencyMs={result.latency_ms} status={result.status} />
    </div>
  );
};

export const ScanResultsSkeleton = () => {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="flex items-center justify-between">
        <div>
          <div className="h-6 w-40 bg-gray-200 rounded" />
          <div className="h-4 w-64 bg-gray-200 rounded mt-2" />
        </div>
        <div className="h-9 w-24 bg-gray-200 rounded" />
      </div>

      <div className="flex items-center gap-4 p-6 bg-white rounded-lg shadow">
        <div className="w-16 h-16 rounded-full bg-gray-200" />
        <div className="space-y-2">
          <div className="h-5 w-24 bg-gray-200 rounded" />
          <div className="h-4 w-32 bg-gray-200 rounded" />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="h-5 w-24 bg-gray-200 rounded mb-3" />
        <div className="h-4 w-full bg-gray-200 rounded" />
        <div className="h-4 w-5/6 bg-gray-200 rounded mt-2" />
        <div className="h-4 w-4/6 bg-gray-200 rounded mt-2" />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="h-5 w-28 bg-gray-200 rounded mb-3" />
        <div className="grid grid-cols-3 gap-3">
          <div className="h-6 bg-gray-200 rounded" />
          <div className="h-6 bg-gray-200 rounded" />
          <div className="h-6 bg-gray-200 rounded" />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="h-5 w-24 bg-gray-200 rounded mb-3" />
        <div className="space-y-2">
          <div className="h-4 w-full bg-gray-200 rounded" />
          <div className="h-4 w-11/12 bg-gray-200 rounded" />
          <div className="h-4 w-10/12 bg-gray-200 rounded" />
        </div>
      </div>
    </div>
  );
}
