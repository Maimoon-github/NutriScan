import type { TrafficLight } from '../types/api';

interface TrafficLightBadgeProps {
  trafficLight: TrafficLight;
}

export const TrafficLightBadge = ({ trafficLight }: TrafficLightBadgeProps) => {
  const colorMap = {
    green: 'bg-traffic-green',
    yellow: 'bg-traffic-yellow',
    red: 'bg-traffic-red',
  };

  const bgColor = colorMap[trafficLight.status];

  return (
    <div className="flex items-center gap-4 p-6 bg-white rounded-lg shadow-md">
      <div className={`w-16 h-16 rounded-full ${bgColor} flex items-center justify-center`}>
        <div className="w-12 h-12 bg-white rounded-full"></div>
      </div>
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{trafficLight.label}</h2>
        <p className="text-sm text-gray-600">Confidence: {(trafficLight.confidence * 100).toFixed(0)}%</p>
      </div>
    </div>
  );
};
