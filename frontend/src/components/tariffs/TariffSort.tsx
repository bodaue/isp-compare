// frontend/src/components/tariffs/TariffSort.tsx
import React from 'react';
import './TariffSort.css';

export type SortOption = {
    value: string;
label: string;
};

export type SortDirection = 'asc' | 'desc';

export type SortConfig = {
    field: string;
direction: SortDirection;
};

interface TariffSortProps {
    onChange: (config: SortConfig) => void;
currentSort: SortConfig;
className?: string;
}

const SORT_OPTIONS: SortOption[] = [
    { value: 'price', label: 'Цена' },
    { value: 'speed', label: 'Скорость' },
    { value: 'name', label: 'Название' },
];

const TariffSort: React.FC<TariffSortProps> = ({ onChange, currentSort, className = '' }) => {
    const handleFieldChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({
        field: e.target.value,
        direction: currentSort.direction,
    });
};

const toggleDirection = () => {
    onChange({
        field: currentSort.field,
        direction: currentSort.direction === 'asc' ? 'desc' : 'asc',
});
};

return (
    <div className={`tariff-sort ${className}`}>
    <div className="sort-controls">
    <select
    value={currentSort.field}
    onChange={handleFieldChange}
    className="sort-select"
    >
    {SORT_OPTIONS.map(option => (
    <option key={option.value} value={option.value}>
    {option.label}
    </option>
))}
</select>

  <button
className="direction-toggle"
onClick={toggleDirection}
aria-label={`Сортировать по ${currentSort.direction === 'asc' ? 'возрастанию' : 'убыванию'}`}
title={`Сортировать по ${currentSort.direction === 'asc' ? 'возрастанию' : 'убыванию'}`}
>
{currentSort.direction === 'asc' ? (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5v14M5 12l7-7 7 7"/>
    </svg>
) : (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5v14M5 12l7 7 7-7"/>
    </svg>
)}
</button>
  </div>
    </div>
);
};

export default TariffSort;