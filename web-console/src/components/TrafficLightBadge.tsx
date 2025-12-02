interface TrafficLightBadgeProps {
  trafficLight: 'green' | 'yellow' | 'red';
  status: 'success' | 'partial_ocr_failure' | 'unreadable';
}

export const TrafficLightBadge = ({ trafficLight, status }: TrafficLightBadgeProps) => {
  const colorMap = {
    green: 'bg-green-100 text-green-900',
    yellow: 'bg-yellow-100 text-yellow-900',
    red: 'bg-red-100 text-red-900',
  };

  const bgColor = colorMap[trafficLight];
  const labelMap = {
    green: 'Good',
    yellow: 'Caution',
    red: 'Avoid',
  } as const;

  return (
    <div className="flex items-center gap-4 p-6 bg-white rounded-lg shadow-md">
      <div className={`w-16 h-16 rounded-full ${bgColor} flex items-center justify-center`}>
        <div className="w-12 h-12 bg-white rounded-full border border-current"></div>
      </div>
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{labelMap[trafficLight]}</h2>
        <p className="text-sm text-gray-700">Status: {status.replace(/_/g, ' ')}</p>
      </div>
    </div>
  );
};
