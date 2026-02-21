import OnboardingContent from '../components/onboardings/OnboardingContent';
import OnboardingFooter from '../components/onboardings/OnboardingFooter';

const OnboardingPage = () => {
  return (
    <div className="w-full h-dvh flex flex-col font-suite">
      <div className="flex-1 min-h-0 overflow-hidden">
        <OnboardingContent />
      </div>
      <OnboardingFooter />
    </div>
  );
};

export default OnboardingPage;
