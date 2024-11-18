import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalFooter,
    ModalBody,
    Button,
    Text,
    useDisclosure
} from '@chakra-ui/react'
import { VscThumbsdown } from 'react-icons/vsc'
import { useTranslation } from 'react-i18next';

const ThumbsDown = ({ OnYesClick, OnNoClick }: { OnYesClick: () => void, OnNoClick: () => void }) => {
    const { t } = useTranslation();
    const { isOpen, onOpen, onClose } = useDisclosure()

    const YesClickHandler = () => {
        OnYesClick();
        onClose()
    }

    const NoClickHandler = () => {
        OnNoClick();
        onClose()
    }

    return (
        <>
            <VscThumbsdown title="Dislike" color="red" size={'1.2em'} cursor={'pointer'} onClick={onOpen} />

            <Modal blockScrollOnMount={false} isOpen={isOpen} onClose={onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalBody>
                        <Text color={'gray.900'}>{t('bad_feedback')}</Text>
                    </ModalBody>

                    <ModalFooter>
                        <Button colorScheme='green' mr={3} onClick={YesClickHandler}>
                            Yes
                        </Button>
                        <Button variant='ghost' onClick={NoClickHandler}>No</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default ThumbsDown;