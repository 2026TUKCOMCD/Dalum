import { useEffect } from 'react';
import useBaseModal from '../stores/modals/baseModal';
import ModalBackground from '../components/modals/ModalBackground';
import LikeInfoModal from '../components/modals/LikeInfoModal';
import DupeResearchModal from '../components/modals/DupeResarchModal';
import LoginModal from '../components/modals/LoginModal';
import WithdrawModal from '../components/modals/WithdrawModal';
import LogoutModal from '../components/modals/LogoutModal';
import GuideModal from '../components/modals/GuideModal';
import SimilarityCheckModal from '../components/modals/SimilarityCheckModal';

const ModalPage = () => {
  const { isModalOpen, modalType } = useBaseModal();

  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isModalOpen]);

  if (!isModalOpen) return null;

  return (
    <>
      <ModalBackground>
        {modalType === 'likeInfoModal' && <LikeInfoModal />}
        {modalType === 'dupeResearchModal' && <DupeResearchModal />}
        {modalType === 'loginModal' && <LoginModal />}
        {modalType === 'withdrawModal' && <WithdrawModal />}
        {modalType === 'logoutModal' && <LogoutModal />}
        {modalType === 'guideModal' && <GuideModal />}
        {modalType === 'similarityCheckModal' && <SimilarityCheckModal />}
      </ModalBackground>
    </>
  );
};

export default ModalPage;
