import React from 'react';
import PageHeader from '../common/PageHeader';

const TariffComparison: React.FC = () => {
    return (
        <div className="page animate-fade-in">
            <PageHeader
                title="Сравнение тарифов"
                subtitle="Сравните параметры и выберите лучший вариант"
            />
            {/* Здесь будет компонент сравнения тарифов */}
        </div>
    );
};

export default TariffComparison;