import { Box, InputGroup, InputRightElement, Spinner, Textarea } from "@chakra-ui/react";
import { VscSend } from "react-icons/vsc";
import {useTranslation} from "react-i18next";

const ChatFooter = ({ inputMessage, setInputMessage, handleSendMessage, aiResponseInprogress, inputRef, isEnabled }:
    { inputMessage: string, setInputMessage: (value: string) => void, handleSendMessage: () => void, aiResponseInprogress: boolean, isEnabled: boolean, inputRef: any }) => {
    const { t } = useTranslation();
    const handleSendClick = async () => {
        if (inputMessage?.trim().length > 0) {
            await handleSendMessage();
        }
    }

    return (
        <InputGroup size='md' >
            <Textarea flex={1} width={'100%'} minH={'45px'}
                placeholder={`${t('ask_your_question')}...`}
                _focus={{
                    border: '0px'
                }}
                onKeyDown={async (e) => {
                    if (e.key === "Enter") {
                        await handleSendMessage();
                    }
                }}
                readOnly={aiResponseInprogress}
                disabled={!isEnabled}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                bgColor={"white"}
                ref={inputRef}
                resize={'none'}
                pr={'4rem'}
                py='3'
            />

            <InputRightElement mx={2} width='3rem'>
                <Box mt={3}>
                    {aiResponseInprogress &&
                        <Spinner color="#2d7150" size={'md'} role="status">
                        </Spinner>}


                    {!aiResponseInprogress &&
                        <VscSend size="1.5em" color={"#2d7150"} cursor={'pointer'} data-testid="btn-send" onClick={handleSendClick} />
                    }
                </Box>
            </InputRightElement>
        </InputGroup>
    );
};

export default ChatFooter;

