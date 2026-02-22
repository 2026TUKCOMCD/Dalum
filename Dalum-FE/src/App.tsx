import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import MainLayout from './layouts/MainLayout';
import SearchPage from './pages/SearchPage';
import ResultPage from './pages/ResultPage';
import ModalPage from './pages/ModalPage';
import MyPage from './pages/MyPage';
import StylingPage from './pages/StylingPage';
import OnboardingPage from './pages/OnboardingPage';
import OnboardingLayout from './layouts/OnboardingLayout';
import OAuthCallbackPage from './pages/OAuthCallbackPage';

function App() {
  return (
    <BrowserRouter>
      <ModalPage />
      <Routes>
        <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
        <Route element={<OnboardingLayout />}>
          <Route path="/" element={<OnboardingPage />} />
        </Route>
        <Route element={<MainLayout />}>
          <Route path="/search" element={<SearchPage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/my" element={<MyPage />} />
          <Route path="/styling" element={<StylingPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
