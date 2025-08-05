import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

interface Props {
  fromMe: boolean;
  text: string;
}

const Bubble = styled(motion.div)<{ fromMe: boolean }>`
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 16px;
  margin-bottom: 0.5rem;
  align-self: ${({ fromMe }) => (fromMe ? 'flex-end' : 'flex-start')};
  background: ${({ fromMe }) => (fromMe ? '#dcf8c6' : '#fff')};
  color: #000;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
`;

const MessageBubble: React.FC<Props> = ({ fromMe, text }) => (
  <Bubble
    fromMe={fromMe}
    initial={{ scale: 0.9, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
  >
    {text}
  </Bubble>
);

export default MessageBubble;