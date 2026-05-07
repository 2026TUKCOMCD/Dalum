import { create } from 'zustand';
import type { BaseModal } from '../../types/modals/Modal.types';

const useBaseModal = create<BaseModal>((set) => ({
  isModalOpen: false,
  modalType: '',
  modalProps: undefined,

  setModalType: (type) => set({ modalType: type }),
  openModal: (type, options) =>
    set({
      isModalOpen: true,
      modalType: type,
      modalProps: options?.props,
    }),
  closeModal: () =>
    set({ isModalOpen: false, modalType: '', modalProps: undefined }),
}));

export default useBaseModal;
