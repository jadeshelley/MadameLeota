#!/usr/bin/env python3
"""
AI Chat System for Madame Leota
Handles AI model loading and response generation
"""

import random
import logging
from typing import Optional

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from ctransformers import AutoModelForCausalLM as CTAutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class MadameLeotaAI:
    """AI system for Madame Leota's responses"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.tokenizer = None
        self.personality = config.get_personality()
        self.ai_config = config.get_ai_config()
        
        # Try to load AI model
        self._load_model()
    
    def _load_model(self):
        """Load the AI model"""
        try:
            if self.ai_config["model_type"] == "local" and TRANSFORMERS_AVAILABLE:
                model_path = self.config.MODELS_DIR / self.ai_config["local_model"]
                
                if model_path.exists():
                    self.logger.info(f"Loading local model: {model_path}")
                    
                    # Try ctransformers first (better for GGUF files)
                    try:
                        self.model = CTAutoModelForCausalLM.from_pretrained(
                            str(model_path),
                            model_type="llama",
                            gpu_layers=0  # CPU only for Pi
                        )
                        self.logger.info("✓ Model loaded with ctransformers")
                    except:
                        # Fallback to transformers
                        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                        self.model = AutoModelForCausalLM.from_pretrained(str(model_path))
                        self.logger.info("✓ Model loaded with transformers")
                        
                else:
                    self.logger.warning(f"Local model not found: {model_path}")
                    self.logger.info("Using template-based responses")
                    
            else:
                self.logger.info("Using template-based responses (no AI model)")
                
        except Exception as e:
            self.logger.error(f"Failed to load AI model: {e}")
            self.logger.info("Using template-based responses")
    
    def get_welcome_message(self) -> str:
        """Get a welcome message from Madame Leota"""
        return random.choice(self.personality["greetings"])
    
    def get_farewell_message(self) -> str:
        """Get a farewell message from Madame Leota"""
        return random.choice(self.personality["farewells"])
    
    def get_response(self, user_input: str) -> str:
        """Generate a response to user input"""
        try:
            if self.model:
                return self._generate_ai_response(user_input)
            else:
                return self._generate_template_response(user_input)
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._generate_fallback_response(user_input)
    
    def _generate_ai_response(self, user_input: str) -> str:
        """Generate response using AI model"""
        try:
            prompt = self._create_prompt(user_input)
            
            if hasattr(self.model, 'generate'):  # transformers
                inputs = self.tokenizer.encode(prompt, return_tensors="pt")
                outputs = self.model.generate(
                    inputs,
                    max_length=len(inputs[0]) + self.ai_config["max_tokens"],
                    temperature=self.ai_config["temperature"],
                    top_p=self.ai_config["top_p"],
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
            else:  # ctransformers
                response = self.model(
                    prompt,
                    max_new_tokens=self.ai_config["max_tokens"],
                    temperature=self.ai_config["temperature"],
                    top_p=self.ai_config["top_p"]
                )
            
            # Extract just the response part
            if prompt in response:
                response = response[len(prompt):].strip()
            
            return self._format_response(response)
            
        except Exception as e:
            self.logger.error(f"AI generation failed: {e}")
            return self._generate_template_response(user_input)
    
    def _create_prompt(self, user_input: str) -> str:
        """Create a prompt for the AI model"""
        personality = self.personality
        
        prompt = f"""You are {personality['name']}, a {personality['style']}. 
You speak in a {personality['tone']} manner.

User: {user_input}

{personality['name']}:"""
        
        return prompt
    
    def _generate_template_response(self, user_input: str) -> str:
        """Generate response using templates"""
        user_input_lower = user_input.lower()
        
        # Fortune templates
        if any(word in user_input_lower for word in ['love', 'romance', 'relationship', 'marriage']):
            return self._get_fortune('love')
        elif any(word in user_input_lower for word in ['career', 'job', 'work', 'business']):
            return self._get_fortune('career')
        elif any(word in user_input_lower for word in ['money', 'wealth', 'fortune', 'financial']):
            return self._get_fortune('wealth')
        else:
            return self._get_fortune('general')
    
    def _get_fortune(self, fortune_type: str) -> str:
        """Get a fortune of the specified type"""
        template = self.personality["fortune_templates"][fortune_type]
        
        fortunes = {
            'love': [
                "a mysterious stranger will enter your life",
                "an old flame may rekindle",
                "love is closer than you think",
                "patience in matters of the heart will be rewarded"
            ],
            'career': [
                "a new opportunity is on the horizon",
                "your hard work will soon be recognized",
                "a change in direction will lead to success",
                "trust your instincts in professional matters"
            ],
            'wealth': [
                "financial prosperity is within reach",
                "an unexpected windfall may come your way",
                "investments made now will bear fruit later",
                "the universe is aligning for your financial success"
            ],
            'general': [
                "the stars are aligning in your favor",
                "a journey will bring unexpected rewards",
                "trust in the signs the universe sends you",
                "your destiny is unfolding exactly as it should"
            ]
        }
        
        detail = random.choice(fortunes[fortune_type])
        return template.format(details=detail)
    
    def _generate_fallback_response(self, user_input: str) -> str:
        """Generate a fallback response when all else fails"""
        fallbacks = [
            "The crystal ball is cloudy today... Let me try again.",
            "The spirits are quiet... Please, ask me something else.",
            "I sense interference in the mystical realm... Can you rephrase that?",
            "The mists of time are unclear... Tell me more about what you seek."
        ]
        return random.choice(fallbacks)
    
    def _format_response(self, response: str) -> str:
        """Format the AI response to match Madame Leota's style"""
        # Clean up the response
        response = response.strip()
        
        # Add mystical touches if not present
        mystical_phrases = [
            "The crystal ball reveals...",
            "I see in the mists...",
            "The spirits tell me...",
            "My mystical senses detect...",
            "The stars align to show..."
        ]
        
        if not any(phrase in response for phrase in mystical_phrases):
            response = f"{random.choice(mystical_phrases)} {response}"
        
        return response
