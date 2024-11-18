import { ChakraProvider } from '@chakra-ui/react';
import { extendTheme } from "@chakra-ui/react";
import { AppInsightsContext } from '@microsoft/applicationinsights-react-js';
import * as React from 'react';
import { reactPlugin } from './appInsights';

const theme = extendTheme({
    colors: {
        brand: {
            900: "#2d7150",
            800: "#688775",
            500: "#c6d3ca",
            50: "#fcfcfc"
        },
    },
    fontSizes: {
        base: "14px",
        xs: "12px",
        sm: "14px",
        md: "16px"
    },
    styles: {
        global: {
            'html, body': {
                fontSize: 'sm',
                fontFamily: 'ui-sans-serif,-apple-system,system-ui,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif,Helvetica,Apple Color Emoji,Arial,Segoe UI Emoji,Segoe UI Symbol',
                backgroundColor:'#c6d3ca'
            },
            // styles for the `body`
            '::-webkit-scrollbar': {
                width: '10px'
            },
            '::-webkit-scrollbar-track': {
                bgColor: '#f1f1f1',
                borderRadius: 5
            },
            '::-webkit-scrollbar-thumb': {
                bgColor: '#888888',
                borderRadius: 5
            },
            '::-webkit-scrollbar-thumb:hover': {
                bgColor: '#555555'
            }
        }
    }
})

export function Providers({
    children
}: {
    children: React.ReactNode
}) {
    return (
        <ChakraProvider theme={theme}>
            <AppInsightsContext.Provider value={reactPlugin}>
                {children}
            </AppInsightsContext.Provider>
        </ChakraProvider>
    )
}