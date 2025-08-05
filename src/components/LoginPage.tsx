import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow: hidden;
`;

const LoginCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 25px 45px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 400px;
  max-width: 90vw;
  position: relative;
`;

const PolarBearContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  height: 120px;
  align-items: center;
`;

const PolarBear = styled(motion.div)`
  width: 80px;
  height: 80px;
  position: relative;
`;

const BearBody = styled(motion.div)`
  width: 60px;
  height: 60px;
  background: #f8f8f8;
  border-radius: 50% 50% 45% 45%;
  position: relative;
  border: 2px solid #e0e0e0;
`;

const BearEar = styled(motion.div)`
  width: 20px;
  height: 20px;
  background: #f8f8f8;
  border-radius: 50%;
  position: absolute;
  border: 2px solid #e0e0e0;
  
  &.left {
    top: -8px;
    left: 8px;
  }
  
  &.right {
    top: -8px;
    right: 8px;
  }
`;

const BearEye = styled(motion.div)`
  width: 8px;
  height: 8px;
  background: #333;
  border-radius: 50%;
  position: absolute;
  top: 18px;
  
  &.left {
    left: 15px;
  }
  
  &.right {
    right: 15px;
  }
`;

const BearPaw = styled(motion.div)`
  width: 25px;
  height: 25px;
  background: #f8f8f8;
  border-radius: 50%;
  border: 2px solid #e0e0e0;
  position: absolute;
  
  &.left {
    left: -15px;
    top: 20px;
  }
  
  &.right {
    right: -15px;
    top: 20px;
  }
`;

const BearNose = styled.div`
  width: 6px;
  height: 4px;
  background: #333;
  border-radius: 2px;
  position: absolute;
  top: 28px;
  left: 50%;
  transform: translateX(-50%);
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const InputGroup = styled.div`
  position: relative;
`;

const Input = styled(motion.input)`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #999;
  }
`;

const Label = styled(motion.label)`
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.8);
  padding: 0 4px;
  color: #666;
  pointer-events: none;
  transition: all 0.3s ease;
  
  ${Input}:focus + &,
  ${Input}:not(:placeholder-shown) + & {
    top: 0;
    font-size: 12px;
    color: #667eea;
  }
`;

const Button = styled(motion.button)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const Title = styled.h1`
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 2rem;
  font-weight: 300;
`;

const LoginPage: React.FC = () => {
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ email: '', password: '' });
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsSubmitting(false);
    alert('Login successful! 🐻');
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const bearVariants = {
    normal: { scale: 1, rotate: 0 },
    hiding: { scale: 0.9, rotate: -5 },
    excited: { scale: 1.1, rotate: [0, -2, 2, 0] }
  };

  const pawVariants = {
    normal: { y: 0, rotate: 0 },
    covering: { y: -15, rotate: -10 }
  };

  return (
    <Container>
      <LoginCard
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <Title>Welcome Back!</Title>
        
        <PolarBearContainer>
          <PolarBear>
            <motion.div
              variants={bearVariants}
              animate={isSubmitting ? "excited" : isPasswordFocused ? "hiding" : "normal"}
              transition={{ duration: 0.3 }}
            >
              <BearBody>
                <BearEar className="left" />
                <BearEar className="right" />
                
                <AnimatePresence>
                  {!isPasswordFocused && (
                    <>
                      <BearEye 
                        className="left"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      />
                      <BearEye 
                        className="right"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      />
                    </>
                  )}
                </AnimatePresence>
                
                <BearNose />
                
                <BearPaw 
                  className="left"
                  variants={pawVariants}
                  animate={isPasswordFocused ? "covering" : "normal"}
                  transition={{ duration: 0.3 }}
                />
                <BearPaw 
                  className="right"
                  variants={pawVariants}
                  animate={isPasswordFocused ? "covering" : "normal"}
                  transition={{ duration: 0.3 }}
                />
              </BearBody>
            </motion.div>
          </PolarBear>
        </PolarBearContainer>

        <Form onSubmit={handleSubmit}>
          <InputGroup>
            <Input
              type="email"
              placeholder=" "
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              required
              whileFocus={{ scale: 1.02 }}
            />
            <Label>Email</Label>
          </InputGroup>

          <InputGroup>
            <Input
              type="password"
              placeholder=" "
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              onFocus={() => setIsPasswordFocused(true)}
              onBlur={() => setIsPasswordFocused(false)}
              required
              whileFocus={{ scale: 1.02 }}
            />
            <Label>Password</Label>
          </InputGroup>

          <Button
            type="submit"
            disabled={isSubmitting}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isSubmitting ? '🐻 Logging in...' : 'Login'}
          </Button>
        </Form>
      </LoginCard>
    </Container>
  );
};

export default LoginPage;