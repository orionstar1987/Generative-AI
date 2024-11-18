import React, { useState } from 'react';
import ReactMarkdown from "react-markdown";
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import ChakraUIRenderer from 'chakra-ui-markdown-renderer';
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw';
import { Link, Button, Spinner } from '@chakra-ui/react';
import { url } from '../lib/constants';
import fetchWrapper from '../lib/fetch-wrapper';
import { useProfile } from '../lib/profileContext';

export const MarkdownViewer: React.FC<{ content: string }> = ({ content }) => {
  const { instance, accounts }: { instance: IPublicClientApplication, accounts: AccountInfo[] } = useMsal();
  const { profile } = useProfile();
  const [document, setDocument] = useState('');

  const newTheme = {
    a: (props: any) => {
      const { href, children } = props;
      if (href.includes("blob.core.windows")) {
        const documentName = decodeURIComponent(href.split('/').pop() || "Download Document");

        return (
          <Button
            size="sm"
            p={2}
            colorScheme="blue"
            onClick={async () => {
              setDocument(documentName);
              try {
                const fw = new fetchWrapper(accounts, instance, profile);
                const response = await fw.getDocument(`${url}/api/document?url=${href}`);
                if (response.status === 200) {
                  const blobUrl = window.URL.createObjectURL(response.data);

                  window.open(blobUrl, '_blank');

                  setTimeout(() => window.URL.revokeObjectURL(blobUrl), 100);
                } else {
                  console.error("Failed to load document");
                }
                setDocument('');
              } catch (error) {
                setDocument('');
                console.error("Error fetching document", error);
              }
            }}
            isDisabled={document === documentName}
            leftIcon={document === documentName ? <Spinner size="xs" /> : undefined}
          >
            {documentName}
          </Button>
        );
      }

      return <Link href={href} color={'blue.500'}>{children}</Link>;
    }
  };

  return (
    <ReactMarkdown components={ChakraUIRenderer(newTheme)}
      children={content}
      skipHtml remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      includeElementIndex={true}
    />
  );
}