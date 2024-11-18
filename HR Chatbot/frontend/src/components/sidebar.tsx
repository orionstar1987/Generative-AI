import { Box, Button, HStack, VStack, useDisclosure, Text, List, ListItem, ListIcon, Collapse, Link } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { MdAdd, MdChat, MdHistory, MdMenu } from 'react-icons/md';
import Settings from './settings';
import fetchWrapper from '../lib/fetch-wrapper';
import { HiOutlineDocumentReport } from 'react-icons/hi';
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import { useProfile } from '../lib/profileContext';
import { useTranslation } from 'react-i18next';
import { url } from '../lib/constants'

const SideBar = ({ onActivityClick, onClearChat, enableSettings, isAdmin }:
    { onActivityClick: (sessionId: string) => void, onClearChat: () => void, enableSettings: boolean, isAdmin: boolean }) => {
    const { t } = useTranslation();
    const { getButtonProps, getDisclosureProps, isOpen } = useDisclosure();
    const [hidden, setHidden] = useState(!isOpen);
    const [sessions, setSessions] = useState<any[]>()
    const [show, setShow] = useState(false)
    const { instance, accounts }: { instance: IPublicClientApplication, accounts: AccountInfo[] } = useMsal();
    const { profile } = useProfile();

    const handleToggle = () => {
        setShow(!show)
    }

    useEffect(() => {
        if (!hidden) {
            const fw = new fetchWrapper(accounts, instance, profile);

            fw.get(`${url}/api/recent`).then((res) => {
                if (res.status === 200) {
                    setSessions(res.data)
                }
            }).catch((ex: any) => {
                console.log(ex)
            });
        }
    }, [hidden])

    return (
        <Box color={'brand.500'} pos={'relative'} height={'calc(100vh - 25px)'}>
            <button {...getButtonProps()}><MdMenu size={'2.5em'} cursor={'pointer'} title={t('expand_menu')} /></button>

            {
                hidden && <><VStack mt={10} gap={10}>
                    <MdAdd size={'2em'} cursor={'pointer'} onClick={onClearChat} title={t('new_chat')} />
                    <MdHistory size={'2em'} cursor={'pointer'} {...getButtonProps()} />

                </VStack>
                    <VStack gap={10} position={'absolute'} bottom={'5px'}>
                        {isAdmin &&
                            <Link href={import.meta.env.VITE_REPORTS_ENDPOINT} target="_blank" >
                                <HiOutlineDocumentReport size={'2em'} cursor={'pointer'} />
                            </Link>
                        }
                        {enableSettings && <Settings />}
                    </VStack>
                </>
            }
            <motion.div
                {...getDisclosureProps()}
                hidden={hidden}
                initial={false}
                onAnimationStart={() => setHidden(false)}
                onAnimationComplete={() => setHidden(!isOpen)}
                animate={{ width: isOpen ? 300 : 0 }}
            >

                <VStack mt={10} gap={10} alignItems={'flex-start'}>
                    <Button leftIcon={<MdAdd />} bg='brand.500' color={'brand.900'} title={t('new_chat')} onClick={onClearChat}>
                        {t('new_chat')}
                    </Button>

                    <VStack h={'calc(100vh - 250px)'} alignItems={'flex-start'}>
                        <HStack>
                            <MdHistory size={'1.5em'} />
                            <Text fontWeight={'600'}>{t('recent_activity')}</Text>
                        </HStack>

                        <Collapse startingHeight={sessions && sessions?.length > 5 ? 200 : 100} in={show}>
                            <List mt={5} maxH={show ? 'calc(100vh - 350px)' : 200} overflowX={show ? 'auto' : undefined}>
                                {
                                    sessions && sessions.map((session) => <ListItem key={session.SessionId} padding={2} cursor={'pointer'} _hover={{ backgroundColor: "brand.500", color: 'brand.900', borderRadius: 5 }} onClick={() => onActivityClick(session.SessionId)}>
                                        <ListIcon as={MdChat} />
                                        {session.Question}
                                    </ListItem>
                                    )
                                }
                            </List>
                        </Collapse>
                        {sessions && sessions?.length > 5 &&
                            <Text fontWeight={'600'} cursor={'pointer'} size='sm' onClick={handleToggle} mt='1rem' ml={3}>
                                {show ? t('show_less') : t('show_more')}
                            </Text>
                        }

                    </VStack>
                    <VStack gap={10} position={'absolute'} bottom={'5px'}>
                        {isAdmin &&
                            <Link href={import.meta.env.VITE_REPORTS_ENDPOINT} target="_blank">
                                <HStack alignItems={'flex-start'}>
                                    <HiOutlineDocumentReport title="Reports" size={'2em'} cursor={'pointer'} />
                                    <Text fontWeight={'600'}>Reports</Text>
                                </HStack>
                            </Link>
                        }
                        {enableSettings &&
                            <HStack>
                                <Settings />
                                <Text fontWeight={'600'}>Adjustments</Text>
                            </HStack>
                        }
                    </VStack>
                </VStack>
            </motion.div>
        </Box>
    );
}

export default SideBar;