type ModalType = string;

export interface BaseModal {
  isModalOpen: boolean;
  modalType: ModalType | string;

  setModalType: (type: ModalType) => void;
  openModal: (type: ModalType) => void;
  closeModal: () => void;
}
