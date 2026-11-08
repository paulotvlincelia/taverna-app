{-# LANGUAGE CPP #-}
{-# LANGUAGE ForeignFunctionInterface #-}

module Simplex.Chat.Mobile.DeviceTest where

#if defined(IOS)
import Foreign.C (CInt (..), CString)
import Foreign.Ptr (Ptr)
import Foreign.StablePtr (StablePtr)
import Simplex.Chat.Controller (ChatConfig (..), ChatController)
import Simplex.Chat.Mobile (cChatMigrateInitWith, defaultMobileConfig)
import Simplex.Chat.Mobile.Shared (CJSONString)

foreign export ccall "chat_migrate_init_device_test" cChatMigrateInitDeviceTest :: CString -> CString -> CInt -> CString -> CInt -> Ptr (StablePtr ChatController) -> IO CJSONString

cChatMigrateInitDeviceTest :: CString -> CString -> CInt -> CString -> CInt -> Ptr (StablePtr ChatController) -> IO CJSONString
cChatMigrateInitDeviceTest = cChatMigrateInitWith defaultMobileConfig {deviceTestSMP = True}
#endif
