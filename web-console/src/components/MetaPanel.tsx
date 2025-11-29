interface MetaPanelProps {
  ocrConfidence: number | null;
  latencyMs: number;
  status: 'success' | 'partial_ocr_failure' | 'unreadable';
}

export const MetaPanel = ({ ocrConfidence, latencyMs, status }: MetaPanelProps) => {
  const statusLabel = status.replace(/_/g, ' ');
  const confidenceStr = ocrConfidence != null ? `${(ocrConfidence * 100).toFixed(1)}%` : 'N/A';
  return (
    <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
      <div className="flex flex-wrap gap-6 justify-between">
        <span>OCR Confidence: {confidenceStr}</span>
        <span>Processing Time: {latencyMs}ms</span>
        <span>Status: {statusLabel}</span>
      </div>
    </div>
  );
};