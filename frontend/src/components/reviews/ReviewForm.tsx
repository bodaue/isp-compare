// frontend/src/components/reviews/ReviewForm.tsx
import React, {useState} from 'react';
import {ReviewCreate} from '../../types/review.types';
import './ReviewForm.css';

interface ReviewFormProps {
    onSubmit: (data: ReviewCreate) => Promise<void>;
    onCancel?: () => void;
    initialRating?: number;
    initialComment?: string;
    submitText?: string;
}

const ReviewForm: React.FC<ReviewFormProps> = ({
                                                   onSubmit,
                                                   onCancel,
                                                   initialRating = 0,
                                                   initialComment = '',
                                                   submitText = 'Отправить отзыв'
                                               }) => {
    const [rating, setRating] = useState(initialRating);
    const [comment, setComment] = useState(initialComment);
    const [hoverRating, setHoverRating] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (rating === 0) {
            setError('Пожалуйста, выберите оценку');
            return;
        }

        if (comment.length < 3) {
            setError('Отзыв должен содержать минимум 3 символа');
            return;
        }

        if (comment.length > 1000) {
            setError('Отзыв не должен превышать 1000 символов');
            return;
        }

        setLoading(true);
        try {
            await onSubmit({rating, comment});
            // Очищаем форму после успешной отправки
            setRating(0);
            setComment('');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Ошибка при отправке отзыва');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form className="review-form" onSubmit={handleSubmit}>
            <div className="form-group">
                <label>Оценка</label>
                <div className="rating-select">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <button
                            key={star}
                            type="button"
                            className={`star-button ${star <= (hoverRating || rating) ? 'active' : ''}`}
                            onClick={() => setRating(star)}
                            onMouseEnter={() => setHoverRating(star)}
                            onMouseLeave={() => setHoverRating(0)}
                        >
                            ★
                        </button>
                    ))}
                </div>
            </div>

            <div className="form-group">
                <label htmlFor="comment">Ваш отзыв</label>
                <textarea
                    id="comment"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Поделитесь своим опытом использования услуг провайдера"
                    rows={4}
                    disabled={loading}
                />
                <div className="character-count">
                    {comment.length}/1000 символов
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="form-actions">
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                >
                    {loading ? 'Отправка...' : submitText}
                </button>
                {onCancel && (
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={onCancel}
                        disabled={loading}
                    >
                        Отмена
                    </button>
                )}
            </div>
        </form>
    );
};

export default ReviewForm;