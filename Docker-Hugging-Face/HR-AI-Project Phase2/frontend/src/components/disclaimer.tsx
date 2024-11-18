import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    Button,
    useDisclosure,
    Text
} from '@chakra-ui/react'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next';

const Disclaimer = ({ agreed }: { agreed: (value:boolean) => void }) => {

    const { isOpen, onOpen, onClose } = useDisclosure();
    const { t } = useTranslation();

   
    useEffect(() => {
        onOpen();
    }, []);  // eslint-disable-line react-hooks/exhaustive-deps

    const disclaimerAgreementHandler = (value: boolean) =>{
        agreed(value);
        onClose();
    }

    return (
        <>
            <Modal isOpen={isOpen} onClose={()=>disclaimerAgreementHandler(false)} closeOnEsc={false} closeOnOverlayClick={false}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>{t('disclaimer_title')}:</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody color={'black'}>
                        <Text mb={2}>{t('disclaimer_first')}</Text>
                        <Text mb={2}>{t('disclaimer_second')}</Text>
                        <Text>{t('disclaimer_third')}</Text>
                    </ModalBody>

                    <ModalFooter>
                        <Button variant='ghost'  mr={3} onClick={()=>disclaimerAgreementHandler(false)}>
                            {t('cancel_btn')}
                        </Button>
                        <Button colorScheme='green' onClick={()=>disclaimerAgreementHandler(true)}>{t('agree_btn')}</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default Disclaimer;