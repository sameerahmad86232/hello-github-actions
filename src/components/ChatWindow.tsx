import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { ChatPreview } from './ChatList';
import MessageBubble from './MessageBubble';

interface Props {
  chat: ChatPreview;
  onBack: () => void;
}

const Container = styled(motion.div)`
  display: flex;
  flex-direction: column;
  height: 100vh;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
`;

const Avatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
`;

const Messages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #e5ddd5;
`;

const InputBar = styled.div`
  display: flex;
  padding: 0.5rem;
  background: #fff;
`;

const TextInput = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 20px;
  margin-right: 0.5rem;
`;

const SendButton = styled.button`
  font-weight: bold;
  color: #009688;
`;

const sampleHistory = [
  { id: 1, author: 'Alice', text: 'Hey there!' },
  { id: 2, author: 'me', text: 'Hello Alice!' },
  { id: 3, author: 'Alice', text: 'How are you doing?' },
];

const ChatWindow: React.FC<Props> = ({ chat, onBack }) => {
  return (
    <Container
      initial={{ x: 30, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -30, opacity: 0 }}
    >
      <Header>
        <button onClick={onBack}>←</button>
        <Avatar src={chat.avatar} alt={chat.name} />
        <h3>{chat.name}</h3>
      </Header>
      <Messages>
        {sampleHistory.map((msg) => (
          <MessageBubble key={msg.id} fromMe={msg.author === 'me'} text={msg.text} />
        ))}
      </Messages>
      <InputBar>
        <TextInput placeholder="Type a message" />
        <SendButton>Send</SendButton>
      </InputBar>
    </Container>
  );
};

export default ChatWindow;