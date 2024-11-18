import {useEffect, useState} from "react";

const Initializer = ({ msalInstance, children }: any) => {
    const [init, setInit] = useState(false);

    useEffect(() => {
        msalInstance.addEventCallback((event: any) => {
            if (event.eventType === 'msal:handleRedirectEnd') {
                setInit(true);
            }
        })
    }, []);

    return init ? children : null;
};

export default Initializer;