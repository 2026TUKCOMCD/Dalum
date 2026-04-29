import StylingContent from "../components/stylings/StylingContent";
import StylingSidebar from "../components/stylings/StylingSdiebar";

const StylingPage = () => {
  return (
    <div className="w-full h-full flex">
      <StylingSidebar />
      <StylingContent />
    </div>
  );
};

export default StylingPage;
