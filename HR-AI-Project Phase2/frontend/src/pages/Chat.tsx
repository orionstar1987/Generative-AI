import { useToast, Box, Flex, Heading, Image, Text, VStack, useDisclosure, IconButton } from '@chakra-ui/react'
import ChatFooter from '../components/chatfooter'
import Messages from '../components/messages';
import { useEffect, useRef, useState } from 'react';
import fetchWrapper from '../lib/fetch-wrapper';
import { v4 as uuidv4 } from 'uuid';
import Disclaimer from '../components/disclaimer';
import { DEFAULT_SYSTEM_MESSAGE, url } from '../lib/constants'
import SideBar from "../components/sidebar";
import { MdFileDownload } from 'react-icons/md';
import BlockingOverlay from '../components/blockingoverrelay';
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import { useProfile } from '../lib/profileContext';
import { useTranslation } from 'react-i18next';

export default function Chat() {
    const { t } = useTranslation();
    const defaultmessage = { role: "assistant", message: t('welcome_message') };
    const [messages, setMessages] = useState<any[]>([defaultmessage]);
    const [inputMessage, setInputMessage] = useState("");
    const [enableSettings, setEnableSettings] = useState(false);
    const [aiResponseInprogress, setAiResponseInprogress] = useState(false);
    const [sessionId, setSessionId] = useState<any>(null)
    const [enableChat, setEnableChat] = useState(true)
    const [loginUserName, setLoginUserName] = useState<any>(null)
    const [isAgreedTerms, setIsAgreedTerms] = useState(true);
    const [isAdmin, setIsAdmin] = useState(false);
    const ref = useRef<HTMLTextAreaElement>(null);
    const toast = useToast();
    const { instance, accounts }: { instance: IPublicClientApplication, accounts: AccountInfo[] } = useMsal();
    const { profile } = useProfile();

    const { isOpen: blocking, onOpen, onClose } = useDisclosure();

    const targetRef = useRef<any>();

    const downloadChat = async () => {
        onOpen()
        await targetRef.current?.exportPdf()
        onClose()
    }

    useEffect(() => {
        ref?.current?.focus();
        const queryParams = new URLSearchParams(window.location.search)
        setEnableSettings(queryParams.get("enableSettings") === 'true')
        createSessionIfNotExists()

    }, []) // eslint-disable-line react-hooks/exhaustive-deps

    const callChatAPI = async (data: any, regenerate = false) => {

        try {

            const fw = new fetchWrapper(accounts, instance, profile);
            setAiResponseInprogress(true)

            const res = await fw.post(`${url}/api/chat`, { ...data, regenerate: regenerate, systemMessage: enableSettings ? JSON.parse(localStorage.getItem('hr-ai-settings') || '{}')?.systemMessage : DEFAULT_SYSTEM_MESSAGE });
            const respMessage = res.data;

            if (res.status === 200) {
               setMessages((old: any[]) => [...old, { role: "assistant", ...respMessage }]);
            }
            else {
                setMessages((old: any[]) => [...old, { role: "assistant", message: respMessage.Message }]);
            }
            setAiResponseInprogress(false)
        } catch (err) {
            setMessages((old: any[]) => [...old, { role: "assistant", message: t('error_occured') }]);
            setAiResponseInprogress(false)
            console.log(err);
        }
    }

    const createSessionIfNotExists = async () => {
        if (!sessionId) {
            try {

                const fw = new fetchWrapper(accounts, instance, profile);

                let newSessionId: string | null = `${uuidv4()}`;

                const res = await fw.post(`${url}/api/session`, { sessionId: newSessionId });

                if (res.status === 200) {
                    const respJson = res.data;
                    setLoginUserName(respJson.user)
                    setIsAdmin(respJson.isAdmin)
                    setSessionId(newSessionId)
                }
                else {
                    setSessionId(null)
                    setIsAdmin(false)
                    newSessionId = null;
                }

                return newSessionId
            } catch (err) {
                setSessionId(null)
                setIsAdmin(false)
                setAiResponseInprogress(false)
                console.log(err);
                return null;
            }
        }
        else {
            return sessionId;
        }
    }

    const handleSendMessage = async () => {
        if (!inputMessage.trim().length) {
            return;
        }

        const currentSessionId = await createSessionIfNotExists()
        if (currentSessionId) {
            const data = { role: "user", message: inputMessage, sessionId: currentSessionId, messageId: `${uuidv4()}` };
            setMessages((old) => [...old, data]);
            setInputMessage("");
            await callChatAPI(data)
        } else {
            toast({
                title: t('session_error_title'),
                description: t('session_error'),
                status: 'error',
                position: 'bottom',
                duration: 5000,
                isClosable: true,
            });
        }

    };

    const handleClearChat = () => {
        setInputMessage("");
        setSessionId(null)
        setMessages([defaultmessage]);
        setEnableChat(true)
    }

    const handleInputMessage = (message: string) => {
        if (message.length <= 500) {
            setInputMessage(message);
        } else {
            setInputMessage(message.substring(0, 500))
        }
    }

    const termsAndConditionsHandler = (agreed: boolean) => {
        setIsAgreedTerms(agreed);
    }

    const messageFeedbackHandler = async (messageId: string, isLiked: Boolean | null, isUpdate: Boolean = false) => {
        const fw = new fetchWrapper(accounts, instance, profile);
        let res = null
        if (!isUpdate) {
            res = await fw.post(`${url}/api/feedback`, { messageId: messageId, isLiked: isLiked });
        }
        else {
            res = await fw.put(`${url}/api/feedback`, { messageId: messageId, isLiked: isLiked });
        }

        if (res.status === 200) {
            setMessages(messages.map((obj) => (
                obj.messageId === messageId && obj.role === 'assistant' ? { ...obj, isLiked: isLiked, submittedFeedback: true } : obj
            )))
        }
    }

    const messageRegenerateHandler = async (messageId: string) => {

        const data = messages.filter((obj) => (
            obj.messageId === messageId && obj.role === 'user')
        )[0];

        setMessages(messages.filter((obj) => (
            obj.messageId !== messageId || (obj.messageId === messageId && obj.role === 'user')
        )))

        await callChatAPI(data, true)
    }

    const activityClickHandler = async (sessionId: string) => {
        try {
            setEnableChat(false)
            const fw = new fetchWrapper(accounts, instance, profile);

            const res = await fw.get(`${url}/api/session/${sessionId}`);

            if (res.status === 200) {
                let messages = res.data;
                messages.unshift(defaultmessage)
                setMessages(messages);
            }
            else {
                handleClearChat()
            }
        } catch (err) {
            handleClearChat()
            console.log(err);
        }
    }

    return (<>{blocking && <BlockingOverlay />}
        <Flex id="app-content" h={'100vh'} backgroundColor="#c6d3ca">
            <Box bg={'brand.900'} p={5}>
            {isAgreedTerms && <SideBar isAdmin={isAdmin} onClearChat={handleClearChat} onActivityClick={activityClickHandler} enableSettings={enableSettings} /> }
            </Box>
            <Box flex={1} px={5}>
                <Box>
                    <Flex direction={'row'} gap={3} mt='5px'>
                        <Image alt="Wind Creek Hospitality" src="/logo.png" mt={'0px'} width={'200px'} height={'100px'} />
                        <Heading size={'xl'} pt={30} textAlign='center' color={'brand.900'} fontWeight={'450'}>AskHR</Heading>
                    </Flex>
                </Box>
                <Box h={'calc(100vh - 205px)'} overflowY={'auto'}>
                    {isAgreedTerms && <>
                        <Box maxW={'1100px'} margin={'auto'} >
                            <Messages ref={targetRef} loginUserName={loginUserName} isEnabled={enableChat} messages={messages} messageFeedbackClick={messageFeedbackHandler} OnMessageRegenerateClick={messageRegenerateHandler} />
                        </Box>
                    </>
                    }
                    {!isAgreedTerms && <Text fontSize={20} mt={10}>{t('please_review_disclaimer')}</Text>}

                </Box>
                {isAgreedTerms &&
                    <Box maxW={'1100px'} margin={'auto'} p={3}>
                            <Flex gap={3}>
                                <VStack flex={'1'}>
                                    <ChatFooter isEnabled={enableChat} aiResponseInprogress={aiResponseInprogress}
                                        inputMessage={inputMessage} handleSendMessage={handleSendMessage}
                                        setInputMessage={handleInputMessage} inputRef={ref}
                                    ></ChatFooter>
                                    <Text color={'brand.900'} fontStyle={'italic'} fontWeight={'600'}>{t('check_for_mistakes')}</Text>
                                </VStack>
                                {enableSettings && <IconButton size={'md'}  _hover={{bgColor:'brand.500', color:'brand.900'}} bgColor={'brand.900'} color={'brand.500'} icon={<MdFileDownload />} onClick={downloadChat} cursor={'pointer'}  aria-label={'Download Chat'} />
                                }
                            </Flex>
                    </Box>
                }
            </Box>


            <Disclaimer agreed={termsAndConditionsHandler} />
        </Flex>
    </>
    )
}