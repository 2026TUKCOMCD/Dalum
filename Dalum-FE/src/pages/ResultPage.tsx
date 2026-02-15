import ResultContent from "../components/results/ResultContent";
import ResultSidebar from "../components/results/ResultSidebar";

const ResultPage = () => {
  return (
    <div className="w-full h-full flex">
      <ResultSidebar />
      <ResultContent />
    </div>
  );
};

export default ResultPage;
