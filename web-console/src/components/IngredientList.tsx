import type { Ingredient } from '../types/api';

interface IngredientListProps {
  ingredients: Ingredient[];
}

export const IngredientList = ({ ingredients }: IngredientListProps) => {
  const riskColors = {
    safe: 'bg-green-100 text-green-800',
    caution: 'bg-yellow-100 text-yellow-800',
    avoid: 'bg-red-100 text-red-800',
    unknown: 'bg-gray-100 text-gray-800',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Ingredients</h3>
      <div className="space-y-2">
        {ingredients.map((ingredient, idx) => (
          <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <div>
              <span className="font-medium text-gray-900">{ingredient.name}</span>
              <span className="text-sm text-gray-600 ml-2">({ingredient.category})</span>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${riskColors[ingredient.risk_level]}`}>
              {ingredient.risk_level}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
