import React, { useState, useRef } from 'react';
import {
    Button,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    Textarea,
    useDisclosure,
    Box,
    HStack,
} from '@chakra-ui/react';
import html2canvas from 'html2canvas';
import { ReactSketchCanvas } from 'react-sketch-canvas';
import fetchWrapper from '../lib/fetch-wrapper';
import { AccountInfo, IPublicClientApplication } from '@azure/msal-browser';
import { useMsal } from '@azure/msal-react';
import { useProfile } from '../lib/profileContext';
import { url } from '../lib/constants';

interface FeedbackFormModalProps {
    targetId: string;
}

const FeedbackFormModal: React.FC<FeedbackFormModalProps> = ({ targetId }) => {
    const { isOpen, onOpen, onClose } = useDisclosure();
    const [feedback, setFeedback] = useState("");
    const [screenshot, setScreenshot] = useState<string | null>(null);
    const [isTakingScreenshot, setIsTakingScreenshot] = useState(false);
    const [showAnnotation, setShowAnnotation] = useState(false);
    const [canvasDimensions, setCanvasDimensions] = useState({ width: 0, height: 0 });
    const canvasRef = useRef<any>(null);
    const { instance, accounts }: { instance: IPublicClientApplication, accounts: AccountInfo[] } = useMsal();
    const { profile } = useProfile();

    const handleScreenshot = async () => {
        setIsTakingScreenshot(true);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            const canvas = await html2canvas(targetElement);
            const screenshotData = canvas.toDataURL('image/png');

            const aspectRatio = canvas.width / canvas.height;
            const maxHeight = 400;
            const adjustedHeight = canvas.height > maxHeight ? maxHeight : canvas.height;
            const adjustedWidth = adjustedHeight * aspectRatio;

            setScreenshot(screenshotData);
            setCanvasDimensions({
                width: adjustedWidth,
                height: adjustedHeight,
            });
            setShowAnnotation(true);

            if (canvasRef.current) {
                canvasRef.current.clearCanvas();
            }
        }
        setIsTakingScreenshot(false);
    };

    const handleRemoveScreenshot = () => {
        setScreenshot(null);
        setShowAnnotation(false);
        if (canvasRef.current) {
            canvasRef.current.clearCanvas();
        }
    };

    const handleModalClose = () => {
        handleRemoveScreenshot();
        setFeedback("");
        onClose();
    };

    const handleUndo = () => {
        if (canvasRef.current) {
            canvasRef.current.undo();
        }
    };

    const handleClearAnnotations = () => {
        if (canvasRef.current) {
            canvasRef.current.clearCanvas();
        }
    };

    const handleSubmit = async () => {
        if (screenshot && canvasRef.current) {
            const annotationCanvas = canvasRef.current.exportImage("png");

            annotationCanvas.then((annotationImage: any) => {
                const combinedImage = new Image();
                combinedImage.src = annotationImage;

                const canvas = document.createElement("canvas");
                canvas.width = canvasDimensions.width;
                canvas.height = canvasDimensions.height;
                const context = canvas.getContext("2d") as CanvasRenderingContext2D;

                const baseImage = new Image();
                baseImage.src = screenshot;
                baseImage.onload = () => {
                    context.drawImage(baseImage, 0, 0, canvas.width, canvas.height);

                    combinedImage.onload = () => {
                        context.drawImage(combinedImage, 0, 0, canvas.width, canvas.height);
                        const combinedScreenshot = canvas.toDataURL("image/png");
                        const fw = new fetchWrapper(accounts, instance, profile);
                        fw.sendFeedback(`${url}/api/submit-feedback`, feedback, combinedScreenshot).then(() => {
                            handleModalClose();
                        }).catch((error) => {
                            console.error("Error:", error)
                            handleModalClose();
                        });
                    };
                };
            });
        }
    };

    return (
        <>
            <Button
                colorScheme="blue"
                onClick={onOpen}
                position="fixed"
                top="20px"
                right="20px"
                zIndex="1000"
            >
                Feedback
            </Button>

            <Modal isOpen={isOpen} onClose={handleModalClose} size="xl">
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Submit Feedback</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Textarea
                            placeholder="Type your feedback here..."
                            value={feedback}
                            onChange={(e) => setFeedback(e.target.value)}
                            mb={4}
                        />
                        <Button
                            onClick={handleScreenshot}
                            isDisabled={isTakingScreenshot}
                            colorScheme="blue"
                            mb={4}
                            mr={4}
                        >
                            {isTakingScreenshot ? "Taking Screenshot..." : "Take Screenshot"}
                        </Button>
                        {screenshot && (
                            <Button colorScheme="red" onClick={handleRemoveScreenshot} mb={4}>
                                Remove Screenshot
                            </Button>
                        )}
                        {showAnnotation && screenshot && (
                            <>
                                <h3>Annotate Screenshot</h3>
                                <Box
                                    width={`${canvasDimensions.width}px`}
                                    height={`${canvasDimensions.height}px`}
                                    maxWidth="100%"
                                    border="1px solid #000"
                                    overflow="hidden"
                                >
                                    <ReactSketchCanvas
                                        ref={canvasRef}
                                        width={`${canvasDimensions.width}px`}
                                        height={`${canvasDimensions.height}px`}
                                        style={{
                                            width: "100%",
                                            height: "100%",
                                        }}
                                        strokeColor="red"
                                        strokeWidth={3}
                                        backgroundImage={screenshot}
                                    />
                                </Box>
                                <HStack spacing={4} mt={4}>
                                    <Button colorScheme="orange" onClick={handleUndo}>
                                        Undo
                                    </Button>
                                    <Button colorScheme="red" onClick={handleClearAnnotations}>
                                        Clear Annotations
                                    </Button>
                                </HStack>
                            </>
                        )}
                    </ModalBody>
                    <ModalFooter>
                        <Button colorScheme="blue" onClick={handleSubmit}>
                            Submit Feedback
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    );
};

export default FeedbackFormModal;
