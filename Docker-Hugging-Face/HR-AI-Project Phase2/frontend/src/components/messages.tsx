import { useEffect, useRef, useState, useImperativeHandle, forwardRef } from "react";
import { Avatar, Box, Divider, Flex, HStack, Spacer, Text, VStack } from "@chakra-ui/react";
import { MarkdownViewer } from "./markdownviewer";
import { AiOutlineUser } from 'react-icons/ai';
import { VscThumbsdown, VscThumbsup, VscThumbsdownFilled, VscThumbsupFilled } from 'react-icons/vsc';
import ThumbsDown from "./thumbsdownmodal";
import { PiCopySimple, PiCopySimpleFill } from "react-icons/pi";
import { CopyToClipboard } from 'react-copy-to-clipboard';
import generatePDF, { Margin, Options, Resolution } from 'react-to-pdf';

const Messages = forwardRef(({ messages, messageFeedbackClick, OnMessageRegenerateClick, isEnabled, loginUserName }:
	{
		messages: any, isEnabled: boolean,
		messageFeedbackClick: (messageId: string, isLiked: Boolean | null, isUpdate: Boolean) => void,
		OnMessageRegenerateClick: (item: any) => void,
		loginUserName: string
	}, ref) => {

	const targetRef = useRef(null);
	const options: Options = {
		method: "save",
		filename: "chat.pdf",
		resolution: Resolution.MEDIUM,
		page: {
			margin: Margin.MEDIUM,
			format: 'A4',
			orientation: 'portrait',
		},
		canvas: {
			mimeType: 'image/png',
			qualityRatio: 1
		},
		overrides: {
			pdf: {
				compress: true
			},
			canvas: {
				useCORS: true
			}
		},
	};

	useImperativeHandle(ref, () => {
		return {
			async exportPdf() {
				await generatePDF(targetRef, options)
			}
		};
	});

	const AlwaysScrollToBottom = () => {
		const elementRef = useRef<HTMLDivElement>(null);
		useEffect(() => {
			if (elementRef.current) {
				elementRef.current.scrollIntoView()
			}
		}, []);
		return <div ref={elementRef} />;
	};

	const messageFeedbackHandler = (item: any, upvote: Boolean) => {
		if (upvote) {
			messageFeedbackClick(item.messageId, item.isLiked == null || item.isLiked === false ? true : null, item.submittedFeedback)
		} else {
			messageFeedbackClick(item.messageId, item.isLiked == null || item.isLiked === true ? false : null, item.submittedFeedback)
		}

	}

	const AssistantMessage = ({ index, item }: { index: number, item: any }) => {

		const [isCopied, setCopied] = useState(false);

		const onCopyToClipBoardClick = () => {
			setCopied(true);
			setTimeout(() => {
				setCopied(false)
			}, 1000);
		}

		return <VStack>
			<MarkdownViewer content={item.message} />
			{item.messageId && <>
				<Divider m={0} />
				<Box w={'100%'}>
					<HStack spacing={3}>
						<Spacer />
						<CopyToClipboard text={item.message} onCopy={onCopyToClipBoardClick}>
							{isCopied ? <PiCopySimpleFill color="brand.900" cursor={'pointer'} size={"1.2em"} title="Copied" /> : <PiCopySimple cursor={'pointer'} size={"1.2em"} title="Copy message" />}
						</CopyToClipboard>
						{isEnabled && <>
							{
								(item.isLiked == null || item.isLiked === false) && <VscThumbsup title="Like" color="green" size={'1.2em'} cursor={'pointer'} onClick={() => messageFeedbackHandler(item, true)} />
							}
							{
								(item.isLiked != null && item.isLiked === true) && <VscThumbsupFilled title="Liked" color="green" size={'1.2em'} cursor={'pointer'} onClick={() => messageFeedbackHandler(item, true)} />
							}
							{
								(item.isLiked == null || item.isLiked === true) &&

								<>
									{index === messages.length - 1 && !item.submittedFeedback && <ThumbsDown OnNoClick={() => messageFeedbackHandler(item, false)} OnYesClick={() => OnMessageRegenerateClick(item.messageId)} />}
									{(index !== messages.length - 1 || item.submittedFeedback) && <VscThumbsdown title="Dislike" color="red" size={'1.2em'} cursor={'pointer'} onClick={() => messageFeedbackHandler(item, false)} />}
								</>
							}
							{
								item.isLiked != null  && item.isLiked === false && <VscThumbsdownFilled title="Disliked" color="red" size={'1.2em'} cursor={'pointer'} onClick={() => messageFeedbackHandler(item, false)} />
							}
						</>
						}
					</HStack>
				</Box>
			</>
			}
		</VStack>
	}
	return (
		<Flex w="100%" flexDirection="column" pr={5} ref={targetRef}>
			{messages?.map((item: any, index: number) => {
				if (item.role === "user") {
					return (
						<Flex key={index} w="100%" justify="flex-end" borderRadius={5}>
							<Flex
								minW="100px"
								maxW="65%"
								my="3"
								p={'3'}
								borderRadius={10}
								bg="brand.50" boxShadow='base' rounded='md'
								className="messagebox-right"
							>
								<Text m={0} p={0}>{item.message}</Text>
							</Flex>
							<Avatar ml={-3} bg="brand.900" color={'brand.500'} name={loginUserName?.split('@')[0].replaceAll('.', ' ')} icon={<AiOutlineUser fontSize='1.5rem' name="User" />}></Avatar>
						</Flex>
					);
				} else {
					return (
						<Flex key={index} w="100%">

							<Avatar src="/assistant.png"
								name="Assistant"
								bg="brand.900"
							></Avatar>
							<Flex
								minW="100px"
								maxW="65%"
								my="3"
								ml="8"
								p="3"
								borderRadius={10}
								bg="brand.50" boxShadow='base' rounded='md'
								className="messagebox-left"
							>
								<Box w={'100%'} overflow={'auto'}>
									<AssistantMessage item={item} index={index} />
								</Box>
							</Flex>
						</Flex>
					);
				}
			})}
			<AlwaysScrollToBottom />
		</Flex>
	);
});

export default Messages;