import Logo from "../../assets/icons/Logo";
import UserIcon from "../../assets/icons/UserIcon";
import useBaseModal from "../../stores/modals/baseModal";
import { Button } from "./Button";

const Header = () => {
  const { openModal } = useBaseModal();
  const accessToken = localStorage.getItem("accessToken");
  return (
    <div className="w-full px-7.5 py-5 bg-secondary-900 flex justify-between items-center shadow-header-shadow border-b border-primary-900">
      <Logo className="w-12.5 text-primary-900" />
      {accessToken ? (
        <UserIcon className="size-7.5 text-primary-900" />
      ) : (
        <Button
          variant="primary"
          size="sm"
          onClick={() => openModal("loginModal")}
        >
          SIGN UP / SIGN IN
        </Button>
      )}
    </div>
  );
};

export default Header;
