import { useState } from 'react';
import type { WhyExplanation, Citation } from '../types/api';

interface WhyAccordionProps {
  why: WhyExplanation;
  citations: Citation[];
}

export const WhyAccordion = ({ why, citations }: WhyAccordionProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">Why this verdict?</h3>
          <p className="text-gray-700">{why.summary}</p>
        </div>
        <svg
          className={`w-6 h-6 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="px-6 pb-6 border-t border-gray-200">
          <div className="pt-4 space-y-4">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Detailed Analysis</h4>
              <ul className="space-y-2">
                {why.details.map((detail, idx) => (
                  <li key={idx} className="text-gray-700 pl-4 border-l-2 border-blue-500">
                    {detail}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Regulatory Basis</h4>
              <p className="text-gray-700">{why.regulatory_basis}</p>
            </div>

            {citations.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Sources & Citations</h4>
                <div className="space-y-2">
                  {citations.map((citation, idx) => (
                    <div key={idx} className="p-3 bg-gray-50 rounded text-sm">
                      <p className="font-medium text-gray-900">{citation.title}</p>
                      <p className="text-gray-600 text-xs mt-1">
                        {citation.source} • {citation.relevance}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
