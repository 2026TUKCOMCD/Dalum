type ModalType = string;

interface ModalOptions {
  props?: Record<string, unknown>;
}

export interface BaseModal {
  isModalOpen: boolean;
  modalType: ModalType | string;
  modalProps?: Record<string, unknown>;

  setModalType: (type: ModalType) => void;
  openModal: (type: ModalType, options?: ModalOptions) => void;
  closeModal: () => void;
}
