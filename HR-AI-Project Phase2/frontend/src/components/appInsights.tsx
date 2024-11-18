import { ApplicationInsights, ITelemetryItem } from '@microsoft/applicationinsights-web';
import { ReactPlugin } from '@microsoft/applicationinsights-react-js';

const reactPlugin = new ReactPlugin();
// const appInsights = new ApplicationInsights({
//     config: {
//         connectionString: import.meta.env.VITE_APPINSIGHTS_CONNECTIONSTRING,
//         extensions: [reactPlugin],
//         extensionConfig: {},
//         enableAutoRouteTracking: true,
//         disableAjaxTracking: false,
//         autoTrackPageVisitTime: true,
//         enableCorsCorrelation: true,
//         enableRequestHeaderTracking: true,
//         enableResponseHeaderTracking: true,
//         disableCookiesUsage: true
//     }
// });
// appInsights.loadAppInsights();
//
// appInsights.addTelemetryInitializer((env: ITelemetryItem) => {
//     env.tags = env.tags || [];
// });

export { reactPlugin };