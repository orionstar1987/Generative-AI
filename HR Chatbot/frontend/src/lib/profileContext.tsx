import React, { createContext, useState, useContext, ReactNode } from 'react';

export interface Profile {
    firstName: string,
    lastName: string,
    email: string,
    property: string,
    employeeId: string,
    department: string,
}

interface ProfileContextType {
    profile: Profile;
    updateProfile: (newProfile: Profile) => void;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

interface ProfileProviderProps {
    children: ReactNode;
}

export const ProfileProvider: React.FC<ProfileProviderProps> = ({ children }) => {
    const [profile, setProfile] = useState<Profile>({
        firstName: '',
        lastName: '',
        email: '',
        property: '',
        employeeId: '',
        department: '',
    });

    const updateProfile = (newProfile: Profile) => {
        setProfile(newProfile);
    };

    return (
        <ProfileContext.Provider value={{ profile, updateProfile }}>
            {children}
        </ProfileContext.Provider>
    );
};

export const useProfile = (): ProfileContextType => {
    const context = useContext(ProfileContext);
    if (!context) {
        throw new Error('useProfile must be used within a ProfileProvider');
    }
    return context;
};
