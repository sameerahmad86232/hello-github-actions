import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

export interface ChatPreview {
  id: string;
  name: string;
  lastMessage: string;
  avatar: string;
}

interface Props {
  chats: ChatPreview[];
  onSelect: (chat: ChatPreview) => void;
}

const List = styled(motion.div)`
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  padding: 1rem;
`;

const Item = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #fff;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`;

const Avatar = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 50%;
`;

const ChatList: React.FC<Props> = ({ chats, onSelect }) => (
  <List
    initial={{ x: -30, opacity: 0 }}
    animate={{ x: 0, opacity: 1 }}
    exit={{ x: 30, opacity: 0 }}
  >
    {chats.map((chat) => (
      <Item
        key={chat.id}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={() => onSelect(chat)}
      >
        <Avatar src={chat.avatar} alt={chat.name} />
        <div>
          <h4>{chat.name}</h4>
          <p>{chat.lastMessage}</p>
        </div>
      </Item>
    ))}
  </List>
);

export default ChatList;