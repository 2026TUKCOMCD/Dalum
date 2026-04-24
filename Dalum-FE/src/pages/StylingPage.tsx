import { useEffect } from 'react';
import StylingContent from '../components/stylings/StylingContent';
import StylingSidebar from '../components/stylings/StylingSdiebar';
import { useStylingStore } from '../stores/stylings/stylingStore';
import { useParams } from 'react-router-dom';

const StylingPage = () => {
  const { stylingId } = useParams();

  const { detailStyling, fetchDetailStyling } = useStylingStore();

  useEffect(() => {
    if (!stylingId) return;

    const id = Number(stylingId);
    if (Number.isNaN(id)) return;

    fetchDetailStyling(id);
  }, [stylingId, fetchDetailStyling]);

  const mainItem = detailStyling?.mainProduct;
  const items = detailStyling?.items ?? [];

  return (
    <div className="w-full h-full flex">
      <StylingSidebar mainItem={mainItem} />
      <StylingContent items={items} />
    </div>
  );
};

export default StylingPage;
