import { useEffect } from 'react';
import { useMeStore } from '../../stores/me/meStore';
import LikeProductCardList from './LikeProductCardList';
import { useProductStore } from '../../stores/products/productStore';

const UserLikedProduct = () => {
  const { likeItem, fetchLikeList } = useMeStore();
  const { updateLikes } = useProductStore();

  useEffect(() => {
    fetchLikeList();
  }, [fetchLikeList]);

  useEffect(() => {
    if (!likeItem) return;
    updateLikes(
      likeItem.map((it) => ({
        id: it.productId,
        isLiked: it.isLiked,
      }))
    );
  }, [likeItem, updateLikes]);

  return (
    <div className="w-full flex flex-col gap-5">
      <span className="typo-body_bold20">좋아요한 제품</span>
      <div className="w-full flex flex-col items-center justify-center gap-5 rounded-sm border-[1.5px] border-gray-500 p-5">
        {likeItem.length === 0 ? (
          <div className="flex flex-col justify-center items-center gap-2.5">
            <span className="typo-body_bold18 text-gray-700">
              좋아요를 등록한 제품이 없어요!
            </span>
            <span className="typo-body_med16 text-gray-600">
              듀프 제품을 검색하고 마음에 드는 제품을 찾아보세요!
            </span>
          </div>
        ) : (
          <LikeProductCardList items={likeItem} />
        )}
      </div>
    </div>
  );
};

export default UserLikedProduct;
