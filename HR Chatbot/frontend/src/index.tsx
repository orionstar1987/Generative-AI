// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import ReactDOM from 'react-dom/client';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import './i18n';

import NoPage from './pages/NoPage';
import Chat from './pages/Chat';
import { Providers } from './components/provider';
import AuthCheck from './components/authCheck';
import { msalConfig } from './lib/authConfig'
import { PublicClientApplication } from '@azure/msal-browser';
import Initializer from './components/initializer';
import { ProfileProvider } from './lib/profileContext';
import FeedbackForm from "./components/feedbackForm";

const msalInstance = new PublicClientApplication(msalConfig);

export default function App() {
    return (
        <Providers>
            <HashRouter>
                <Routes>
                    <Route path="/">
                        <Route index element={<AuthCheck><><Chat /><FeedbackForm targetId="app-content" /></></AuthCheck>} />
                        <Route path="*" element={<AuthCheck><NoPage /></AuthCheck>} />
                    </Route>
                </Routes>
            </HashRouter>
        </Providers>
    );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <>
        <MsalProvider instance={msalInstance}>
            <Initializer msalInstance={msalInstance}>
                <ProfileProvider>
                    <App />
                </ProfileProvider>
            </Initializer>
        </MsalProvider>
    </>
);
