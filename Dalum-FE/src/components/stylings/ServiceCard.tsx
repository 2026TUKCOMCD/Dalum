import Logo from '../../assets/icons/Logo';
import MiniLogo from '../../assets/icons/MiniLogo';

const ServiceCard = () => {
  return (
    <div className="w-55 h-55 flex flex-col items-center justify-center gap-4 bg-gray-0 rounded-lg border border-primary-600">
      <span className="typo-body_bold16 text-primary-900 text-center">
        나에게 어울리는
        <br />
        스타일을
        <br />더 정확하게!
      </span>
      <div className="flex items-center justify-center gap-2.5">
        <MiniLogo className="h-10" />
        <Logo className="w-20 text-primary-900" />
      </div>
    </div>
  );
};

export default ServiceCard;
