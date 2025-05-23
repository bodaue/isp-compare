// frontend/src/components/reviews/ReviewList.tsx
import React, {useEffect, useState} from 'react';
import {reviewService} from '../../services/reviewService';
import {Review} from '../../types/review.types';
import ReviewCard from './ReviewCard';
import ReviewForm from './ReviewForm';
import {useAuth} from '../../contexts/AuthContext';
import Modal from '../common/Modal';
import './ReviewList.css';

interface ReviewListProps {
    providerId: string;
    onReviewChange?: () => void; // Новый пропс для обновления информации о провайдере
}

const ReviewList: React.FC<ReviewListProps> = ({providerId, onReviewChange}) => {
    const [reviews, setReviews] = useState<Review[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingReview, setEditingReview] = useState<Review | null>(null);
    const [userReview, setUserReview] = useState<Review | null>(null);
    const {isLoggedIn} = useAuth();
    const limit = 10;

    // Извлекаем ID текущего пользователя из localStorage
    const getCurrentUserId = () => {
        const token = localStorage.getItem('accessToken');
        if (!token) return null;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.sub;
        } catch {
            return null;
        }
    };

    useEffect(() => {
        fetchReviews(0, true);
    }, [providerId]);

    const fetchReviews = async (pageNum: number = 0, reset: boolean = true) => {
        try {
            setLoading(true);
            const offset = pageNum * limit;
            const data = await reviewService.getProviderReviews(
                providerId,
                limit,
                offset
            );

            if (reset) {
                setReviews(data);
            } else {
                setReviews(prev => [...prev, ...data]);
            }

            setHasMore(data.length === limit);
            setPage(pageNum);

            // Найдем отзыв текущего пользователя
            const currentUserId = getCurrentUserId();
            if (currentUserId) {
                const userReviewData = data.find(review => review.user?.id === currentUserId) ||
                    reviews.find(review => review.user?.id === currentUserId);
                setUserReview(userReviewData || null);
            }
        } catch (error) {
            console.error('Error fetching reviews:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadMore = async () => {
        const nextPage = page + 1;
        await fetchReviews(nextPage, false);
    };

    const handleCreateReview = async (data: any) => {
        try {
            await reviewService.createReview(providerId, data);
            await fetchReviews();
            if (onReviewChange) onReviewChange(); // Обновляем данные провайдера
            setShowForm(false);
        } catch (err: any) {
            console.error('Error creating review:', err);
        }
    };

    const handleUpdateReview = async (data: any) => {
        if (!editingReview) return;
        try {
            await reviewService.updateReview(editingReview.id, data);
            await fetchReviews();
            if (onReviewChange) onReviewChange(); // Обновляем данные провайдера
            setEditingReview(null);
        } catch (err: any) {
            console.error('Error updating review:', err);
        }
    };

    const handleDeleteReview = async (reviewId: string) => {
        if (window.confirm('Вы уверены, что хотите удалить отзыв?')) {
            try {
                await reviewService.deleteReview(reviewId);
                await fetchReviews();
                if (onReviewChange) onReviewChange(); // Обновляем данные провайдера
            } catch (err: any) {
                console.error('Error deleting review:', err);
            }
        }
    };

    const currentUserId = getCurrentUserId();

    return (
        <div className="review-list">
            <div className="review-list-header">
                <h2>Отзывы</h2>
                {/* Показываем кнопку только если есть отзывы */}
                {isLoggedIn && !userReview && reviews.length > 0 && !showForm && (
                    <button
                        className="btn btn-primary btn-compact"
                        onClick={() => setShowForm(true)}
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                             strokeWidth="2">
                            <path d="M12 5v14M5 12h14"/>
                        </svg>
                        Написать отзыв
                    </button>
                )}
            </div>

            {showForm && (
                <ReviewForm
                    onSubmit={handleCreateReview}
                    onCancel={() => setShowForm(false)}
                />
            )}

            {loading && reviews.length === 0 ? (
                <div className="reviews-loading">
                    <div className="loading-spinner"></div>
                    Загрузка отзывов...
                </div>
            ) : reviews.length === 0 ? (
                <div className="no-reviews">
                    <p>Пока нет отзывов о провайдере</p>
                    {isLoggedIn && !showForm && (
                        <button
                            className="btn btn-primary btn-compact"
                            onClick={() => setShowForm(true)}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                            &nbsp;&nbsp;Написать первый отзыв
                        </button>
                    )}
                </div>
            ) : (
                <>
                    <div className="reviews-grid">
                        {reviews.map((review) => (
                            <ReviewCard
                                key={review.id}
                                review={review}
                                showActions={currentUserId === review.user?.id}
                                onEdit={() => setEditingReview(review)}
                                onDelete={() => handleDeleteReview(review.id)}
                            />
                        ))}
                    </div>

                    {hasMore && (
                        <div className="load-more">
                            <button
                                className="btn btn-secondary btn-sm"
                                onClick={loadMore}
                                disabled={loading}
                            >
                                {loading ? 'Загрузка...' : 'Показать еще'}
                            </button>
                        </div>
                    )}
                </>
            )}

            <Modal
                isOpen={!!editingReview}
                onClose={() => setEditingReview(null)}
                title="Редактировать отзыв"
            >
                {editingReview && (
                    <ReviewForm
                        onSubmit={handleUpdateReview}
                        onCancel={() => setEditingReview(null)}
                        initialRating={editingReview.rating}
                        initialComment={editingReview.comment}
                        submitText="Сохранить изменения"
                    />
                )}
            </Modal>
        </div>
    );
};

export default ReviewList;