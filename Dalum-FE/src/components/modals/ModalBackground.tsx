import useBaseModal from "../../stores/modals/baseModal";
import React, { useEffect } from "react";

interface ModalBackgroundProps {
  children: React.ReactNode;
}

const ModalBackground = ({ children }: ModalBackgroundProps) => {
  const { closeModal } = useBaseModal();

  const preventScroll = () => {
    document.documentElement.style.overflow = "hidden";
  };

  const allowScroll = () => {
    document.documentElement.style.overflow = "auto";
  };

  useEffect(() => {
    preventScroll();
    return () => {
      allowScroll();
    };
  }, []);

  return (
    <div
      onClick={() => closeModal()}
      className="w-full fixed inset-0 mx-auto bg-screen-modal z-50 overflow-hidden"
    >
      <div className={`h-full w-full flex justify-center items-center`}>
        <div onClick={(e) => e.stopPropagation()}>{children}</div>
      </div>
    </div>
  );
};

export default ModalBackground;
