import {
  Box, FormControl, FormLabel, Switch, Textarea, useDisclosure,
  Drawer,
  DrawerBody,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
} from '@chakra-ui/react'

import { useEffect, useState } from 'react'
import { DEFAULT_SYSTEM_MESSAGE } from '../lib/constants'
import { HiOutlineAdjustmentsHorizontal } from 'react-icons/hi2'

const Settings = () => {

  const defaultSettings = {
    systemMessage: DEFAULT_SYSTEM_MESSAGE,
    customizeSystemMessage: false
  }
  const [settings, setSettings] = useState(defaultSettings)
  useEffect(() => {
    if (settings.customizeSystemMessage) {
      localStorage.setItem('hr-ai-settings', JSON.stringify(settings));
    } 
  }, [settings]);

  useEffect(() => {
    const hrAiSettings = localStorage.getItem('hr-ai-settings');
    if (hrAiSettings) {
      setSettings(JSON.parse(hrAiSettings));
    } else {
      setSettings(defaultSettings)
      localStorage.setItem('hr-ai-settings', JSON.stringify(defaultSettings));
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleCustomSystemMessageSwitch = (event: any) => {
    if (event.target.checked) {
      setSettings({ ...settings, customizeSystemMessage: event.target.checked })
    }
    else {
      setSettings({ ...settings, systemMessage: DEFAULT_SYSTEM_MESSAGE, customizeSystemMessage: event.target.checked })
    }
  }

  const handleSystemMessageChange = (event: any) => {
    setSettings({ ...settings, systemMessage: event.target.value })
  }

  const { isOpen, onOpen, onClose } = useDisclosure()

  return (
    <>
      <HiOutlineAdjustmentsHorizontal size={'2em'} cursor={'pointer'} onClick={onOpen} title={"Adjustments"} />
      <Drawer
        isOpen={isOpen}
        placement='right'
        onClose={onClose} size={'lg'} colorScheme='green'>
        <DrawerOverlay />
        <DrawerContent bg={'brand.50'} color={'brand.800'}>
          <DrawerCloseButton name='Close'/>
          <DrawerHeader>Settings</DrawerHeader>

          <DrawerBody>
            <FormControl display='flex' alignItems='center' mb={5}>
              <FormLabel htmlFor='custom-system-message' mb='0'>
                Customize System Message?
              </FormLabel>
              <Switch id='custom-system-message' size={'lg'} colorScheme="green" isChecked={settings.customizeSystemMessage} onChange={handleCustomSystemMessageSwitch} />
            </FormControl>

            <Box visibility={settings.customizeSystemMessage ? 'visible' : 'hidden'}>
              <Textarea data-testid='system-prompt' bg={'white'} onChange={handleSystemMessageChange} value={settings.systemMessage} minH={'300px'} minW={'90%'} >
              </Textarea>
            </Box>
          </DrawerBody>

          <DrawerFooter>

          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    </>
  )

}

export default Settings;