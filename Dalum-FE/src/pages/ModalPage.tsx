import { useEffect } from "react";
import useBaseModal from "../stores/modals/baseModal";
import ModalBackground from "../components/modals/ModalBackground";
import LikeInfoModal from "../components/modals/LikeInfoModal";
import DupeResearchModal from "../components/modals/DupeResarchModal";

const ModalPage = () => {
  const { isModalOpen, modalType } = useBaseModal();

  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [isModalOpen]);

  if (!isModalOpen) return null;

  return (
    <>
      <ModalBackground>
        {modalType === "likeInfoModal" && <LikeInfoModal />}
        {modalType === "dupeResearchModal" && <DupeResearchModal />}
      </ModalBackground>
    </>
  );
};

export default ModalPage;
