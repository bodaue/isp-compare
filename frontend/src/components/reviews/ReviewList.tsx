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
}

const ReviewList: React.FC<ReviewListProps> = ({providerId}) => {
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
        fetchReviews();
    }, [providerId]);

    const fetchReviews = async (reset: boolean = true) => {
        try {
            setLoading(true);
            const currentPage = reset ? 0 : page;
            const data = await reviewService.getProviderReviews(
                providerId,
                limit,
                currentPage * limit
            );

            if (reset) {
                setReviews(data);
            } else {
                setReviews(prev => [...prev, ...data]);
            }

            setHasMore(data.length === limit);
            setPage(reset ? 0 : currentPage);

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
        setPage(nextPage);
        await fetchReviews(false);
    };

    const handleCreateReview = async (data: any) => {
        await reviewService.createReview(providerId, data);
        await fetchReviews();
        setShowForm(false);
    };

    const handleUpdateReview = async (data: any) => {
        if (!editingReview) return;
        await reviewService.updateReview(editingReview.id, data);
        await fetchReviews();
        setEditingReview(null);
    };

    const handleDeleteReview = async (reviewId: string) => {
        if (window.confirm('Вы уверены, что хотите удалить отзыв?')) {
            await reviewService.deleteReview(reviewId);
            await fetchReviews();
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
                        className="btn btn-primary btn-sm"
                        onClick={() => setShowForm(true)}
                    >
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
                            className="btn btn-primary btn-sm"
                            onClick={() => setShowForm(true)}
                        >
                            Написать первый отзыв
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