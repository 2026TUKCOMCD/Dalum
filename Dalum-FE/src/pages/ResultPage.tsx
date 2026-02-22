import { useParams } from 'react-router-dom';
import ResultContent from '../components/results/ResultContent';
import ResultSidebar from '../components/results/ResultSidebar';
import { useMeStore } from '../stores/me/meStore';
import { useEffect } from 'react';
import { useProductStore } from '../stores/products/productStore';

const ResultPage = () => {
  const { searchId } = useParams();
  const { updateLikes } = useProductStore();
  const isDetail = Boolean(searchId);

  const { detailDupeSearchList, fetchDetailDupeSearchList } = useMeStore();

  useEffect(() => {
    if (!detailDupeSearchList) return;
    updateLikes(
      detailDupeSearchList.results.map((it) => ({
        id: it.productId,
        isLiked: it.isLiked,
      }))
    );
  }, [detailDupeSearchList, updateLikes]);

  useEffect(() => {
    if (!isDetail) return;

    const id = Number(searchId);
    if (Number.isNaN(id)) return;

    fetchDetailDupeSearchList(id);
  }, [isDetail, searchId, fetchDetailDupeSearchList]);

  const imageUrl = detailDupeSearchList?.imageUrl;
  const items = detailDupeSearchList?.results ?? [];

  return (
    <div className="w-full h-full flex">
      <ResultSidebar imageUrl={imageUrl} />
      <ResultContent items={items} />
    </div>
  );
};

export default ResultPage;
