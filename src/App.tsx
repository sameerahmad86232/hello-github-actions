import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import ChatList, { ChatPreview } from './components/ChatList';
import ChatWindow from './components/ChatWindow';

const sampleChats: ChatPreview[] = [
  {
    id: '1',
    name: 'Alice',
    lastMessage: 'Hey there!',
    avatar: 'https://i.pravatar.cc/150?img=32',
  },
  {
    id: '2',
    name: 'Bob',
    lastMessage: 'How are you?',
    avatar: 'https://i.pravatar.cc/150?img=12',
  },
];

const App: React.FC = () => {
  const [activeChat, setActiveChat] = useState<ChatPreview | null>(null);

  return (
    <AnimatePresence mode="wait">
      {activeChat ? (
        <ChatWindow
          key={activeChat.id}
          chat={activeChat}
          onBack={() => setActiveChat(null)}
        />
      ) : (
        <ChatList
          key="chat-list"
          chats={sampleChats}
          onSelect={(chat) => setActiveChat(chat)}
        />
      )}
    </AnimatePresence>
  );
};

export default App;