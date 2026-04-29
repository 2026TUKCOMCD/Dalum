import { useEffect } from 'react';
import StylingContent from '../components/stylings/StylingContent';
import StylingSidebar from '../components/stylings/StylingSdiebar';
import { useStylingStore } from '../stores/stylings/stylingStore';
import { useParams } from 'react-router-dom';

const StylingPage = () => {
  const { stylingId } = useParams();

  const { stylingResult, detailStyling, fetchDetailStyling } =
    useStylingStore();

  useEffect(() => {
    if (!stylingId) return;

    const id = Number(stylingId);
    if (Number.isNaN(id)) return;

    fetchDetailStyling(id);
  }, [stylingId, fetchDetailStyling]);

  const mainItem = detailStyling?.mainProduct || stylingResult?.mainProduct;
  const items = detailStyling?.items ?? [];

  console.log('StylingCardList items', mainItem?.category);
  console.log('mainItem:', mainItem);

  return (
    <div className="w-full h-full flex">
      <StylingSidebar mainItem={mainItem} />
      <StylingContent items={items} mainItem={mainItem!} />
    </div>
  );
};

export default StylingPage;
