import { create } from "zustand";
import type { BaseModal } from "../../types/modals/Modal.types";

const useBaseModal = create<BaseModal>((set) => ({
  isModalOpen: false,
  modalType: "",

  setModalType: (type) => set({ modalType: type }),
  openModal: (type) =>
    set({
      isModalOpen: true,
      modalType: type,
    }),

  closeModal: () => set({ isModalOpen: false, modalType: "" }),
}));

export default useBaseModal;
