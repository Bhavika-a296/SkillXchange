import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { RealtimeProvider } from './contexts/RealtimeContext';
import Navbar from './components/Navigation/Navbar';
import NotificationManager from './components/NotificationManager/NotificationManager';
import Home from './pages/Home';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import Profile from './pages/Profile/Profile';
import UserProfileView from './pages/Profile/UserProfileView';
import Skills from './pages/Skills/Skills';
import Messages from './pages/Messages/Messages';
import Notifications from './pages/Notifications/Notifications';
import Learning from './pages/Learning/Learning';
import LearningRequests from './components/LearningRequests/LearningRequests';
import Rating from './pages/Rating/Rating';
import ResumeUpload from './components/ResumeUpload/ResumeUpload';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <RealtimeProvider>
        <Router>
          <div className="app">
            <Navbar />
            <NotificationManager />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <Profile />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/skills"
                  element={
                    <ProtectedRoute>
                      <Skills />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/messages"
                  element={
                    <ProtectedRoute>
                      <Messages />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/notifications"
                  element={
                    <ProtectedRoute>
                      <Notifications />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/learning"
                  element={
                    <ProtectedRoute>
                      <Learning />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/learning-requests"
                  element={
                    <ProtectedRoute>
                      <LearningRequests />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/rate-session/:sessionId"
                  element={
                    <ProtectedRoute>
                      <Rating />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/users/:username"
                  element={
                    <ProtectedRoute>
                      <UserProfileView />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/upload-resume"
                  element={
                    <ProtectedRoute>
                      <ResumeUpload />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
          </div>
        </Router>
      </RealtimeProvider>
    </AuthProvider>
  );
}

export default App;
