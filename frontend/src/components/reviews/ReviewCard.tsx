import React from 'react';
import {Review} from '../../types/review.types';
import './ReviewCard.css';

interface ReviewCardProps {
    review: Review;
    onEdit?: () => void;
    onDelete?: () => void;
    showActions?: boolean;
}

const ReviewCard: React.FC<ReviewCardProps> = ({review, onEdit, onDelete, showActions = false}) => {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    return (
        <div className="review-card">
            <div className="review-header">
                <div className="review-user">
                    <div className="review-avatar">
                        {review.user?.fullname.charAt(0) || 'A'}
                    </div>
                    <div className="review-user-info">
                        <h4>{review.user?.fullname || 'Анонимный пользователь'}</h4>
                        <span className="review-date">{formatDate(review.created_at)}</span>
                    </div>
                </div>
                <div className="review-rating">
                    {[...Array(5)].map((_, index) => (
                        <span
                            key={index}
                            className={`star ${index < review.rating ? 'filled' : ''}`}
                        >
                            ★
                        </span>
                    ))}
                </div>
            </div>
            <div className="review-content">
                <p>{review.comment}</p>
            </div>
            {showActions && (
                <div className="review-actions">
                    <button
                        className="btn-action btn-edit"
                        onClick={onEdit}
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                             strokeWidth="2">
                            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                        </svg>
                        Редактировать
                    </button>
                    <button
                        className="btn-action btn-delete"
                        onClick={onDelete}
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                             strokeWidth="2">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path
                                d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                        Удалить
                    </button>
                </div>
            )}
        </div>
    );
};

export default ReviewCard;