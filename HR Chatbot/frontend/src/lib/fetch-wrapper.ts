import axios from 'axios';
import { loginRequest } from './authConfig';
import { AccountInfo, AuthenticationResult, IPublicClientApplication } from '@azure/msal-browser';
import { Profile } from './profileContext';

type Headers = {
    Authorization: string;
    'x-profile-token': string;
    'x-profile-test'?: string
};

export default class fetchWrapper {
    constructor(private accounts: AccountInfo[], private instance: IPublicClientApplication, private profile?: Profile) {

    }
    async get(url: string, headers: any = {}) {
        const tokens = await this.fetchAccessToken();
        headers = {
            'Authorization': `Bearer ${tokens.idToken}`,
            'x-profile-token': tokens.accessToken,
            ...headers
        };
        if (import.meta.env.VITE_TEST && this.profile) {
            headers['x-profile-test'] = JSON.stringify(this.profile)
        }
        return axios.get(url, { headers });
    }

    async post(url: string, body: any, headers: any = {}, serialize: boolean = true) {
        if (serialize) {
            headers = {
                'Content-Type': 'application/json',
                ...headers
            }
        }
        const tokens = await this.fetchAccessToken();
        headers = {
            'Authorization': `Bearer ${tokens.idToken}`,
            'x-profile-token': tokens.accessToken,
            ...headers
        };
        if (import.meta.env.VITE_TEST && this.profile) {
            headers['x-profile-test'] = JSON.stringify(this.profile)
        }
        return axios.post(url, serialize ? JSON.stringify(body) : body, { headers });
    }

    async put(url: string, body: any, headers: any = {}, serialize: boolean = true) {
        if (serialize) {
            headers = {
                'Content-Type': 'application/json',
                ...headers
            }
        }
        const tokens = await this.fetchAccessToken();
        headers = {
            'Authorization': `Bearer ${tokens.idToken}`,
            'x-profile-token': tokens.accessToken,
            ...headers
        };
        if (import.meta.env.VITE_TEST && this.profile) {
            headers['x-profile-test'] = JSON.stringify(this.profile)
        }
        return axios.put(url, JSON.stringify(body), { headers });
    }

    async delete(url: string, headers: any = {}) {
        const tokens = await this.fetchAccessToken();
        headers = {
            'Authorization': `Bearer ${tokens.idToken}`,
            'x-profile-token': tokens.accessToken,
            ...headers
        };
        if (import.meta.env.VITE_TEST && this.profile) {
            headers['x-profile-test'] = JSON.stringify(this.profile)
        }
        return axios.delete(url, { headers });
    }

    async getProfile() {
        const headers = {
            'Authorization': `Bearer ${(await this.fetchAccessToken()).accessToken}`
        };
        return axios.get('https://graph.microsoft.com/v1.0/me?$select=givenName,surname,mail,officeLocation,employeeId,department', { headers });
    }

    async fetchAccessToken(): Promise<{ idToken: string, accessToken: string }> {
        if (this.accounts.length > 0) {
            try {
                const response = await this.instance.acquireTokenSilent({
                    ...loginRequest,
                    account: this.accounts[0],
                });
                return {
                    idToken: response.idToken,
                    accessToken: response.accessToken
                };
            } catch (error) {
                await this.instance.loginRedirect(loginRequest);
            }
        }
        return {
            idToken: '',
            accessToken: ''
        };
    }

    async getDocument(url: string) {
        const tokens = await this.fetchAccessToken();
        const headers: Headers = {
            'Authorization': `Bearer ${tokens.idToken}`,
            'x-profile-token': tokens.accessToken,
        };
        if (import.meta.env.VITE_TEST && this.profile) {
            headers['x-profile-test'] = JSON.stringify(this.profile)
        }
        return axios.get(url, { headers, responseType: 'blob' });
    }

    async sendFeedback(url: string, feedback: string | null, screenshot: string | null){
        const tokens = await this.fetchAccessToken();
        const headers: Headers = {
            'Authorization': `Bearer ${tokens.idToken}`,
            'x-profile-token': tokens.accessToken,
        };
        if (import.meta.env.VITE_TEST && this.profile) {
            headers['x-profile-test'] = JSON.stringify(this.profile)
        }
        return axios.post(url, { feedback, screenshot }, { headers });
    }
}