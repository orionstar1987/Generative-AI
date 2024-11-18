import { useEffect, useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../lib/authConfig';
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import fetchWrapper from '../lib/fetch-wrapper';
import { useProfile } from '../lib/profileContext';
import { useTranslation } from 'react-i18next';
import { propertiesLng } from '../lib/constants';

const AuthCheck = ({ children }: any) => {
  const { instance, accounts }: { instance: IPublicClientApplication, accounts: AccountInfo[] } = useMsal();
  const [authorized, setAuthorized] = useState(false);
  const { updateProfile } = useProfile();
  const { t, i18n } = useTranslation();

  const fetchAccessToken = async () => {
    if (accounts.length > 0) {
      try {
        const response = await instance.acquireTokenSilent({
          ...loginRequest,
          account: accounts[0],
        });
        return response.idToken;
      } catch (error) {
        return instance.loginRedirect(loginRequest);
      }
    }
    return null;
  };

  useEffect(() => {
    const fetchToken = async () => {
      if (accounts.length === 0) {
          await instance.loginRedirect(loginRequest)
      } else {
        await fetchAccessToken();
        const fw = new fetchWrapper(accounts, instance)
        const profile = await fw.getProfile();
        const storage_profile = localStorage.getItem('profile')
        const profileState = storage_profile ? JSON.parse(storage_profile) : {
          firstName: profile.data.givenName,
          lastName: profile.data.surname,
          email: profile.data.mail,
          property: profile.data.officeLocation,
          employeeId: profile.data.employeeId,
          department: profile.data.department
        }
        updateProfile(profileState);
        await i18n.changeLanguage(propertiesLng[profileState.property]);

        setAuthorized(true);
      }
    };

    void fetchToken();
  }, [accounts, instance]);

  return (
    <div className="App">
      {authorized ? children : null}
    </div>
  );
}

export default AuthCheck;