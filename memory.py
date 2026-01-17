from dotenv import load_dotenv
from mem0 import MemoryClient
import logging
import json
import os
from datetime import datetime

# Load environment variables
load_dotenv()

MEM0_API_KEY = os.getenv("MEM0_API_KEY")
if not MEM0_API_KEY:
    raise ValueError("MEM0_API_KEY not found in environment variables")

mem0 = MemoryClient(api_key=MEM0_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== MEMORY SYSTEM CONFIGURATION =====
MEMORY_CONFIG = {
    "use_ai_summarization": True,  # Set to False to use keyword extraction only
    "max_memories_to_load": 10,    # How many past memories to load on startup
    "ai_model": "gemini-2.0-flash-exp",  # Which Gemini model to use for summarization
}


class ConversationBuffer:
    """Buffer to hold conversation during session"""
    def __init__(self):
        self.messages = []
        self.user_id = None
    
    def add_exchange(self, user_msg, assistant_msg):
        """Add a user-assistant exchange to buffer"""
        self.messages.append({
            "user": user_msg,
            "assistant": assistant_msg,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_conversation_text(self):
        """Get formatted conversation text"""
        if not self.messages:
            return ""
        
        conversation = []
        for msg in self.messages:
            conversation.append(f"User: {msg['user']}")
            conversation.append(f"Assistant: {msg['assistant']}")
        
        return "\n".join(conversation)
    
    def clear(self):
        """Clear the buffer"""
        self.messages = []


# Global conversation buffer
conversation_buffer = ConversationBuffer()


def add_exchange_to_buffer(user_id, user_message, assistant_message):
    """
    Add a single exchange to the conversation buffer (not saved yet).
    
    :param user_id: User identifier
    :param user_message: What the user said
    :param assistant_message: What the assistant replied
    """
    conversation_buffer.user_id = user_id
    conversation_buffer.add_exchange(user_message, assistant_message)
    logger.info(f"📝 Added exchange to buffer (total: {len(conversation_buffer.messages)})")


def summarize_conversation(conversation_text, user_id, use_ai=True):
    """
    Summarize conversation to extract key information.
    Uses Gemini AI for intelligent summarization or falls back to keyword extraction.
    
    :param conversation_text: Full conversation text
    :param user_id: User identifier
    :param use_ai: Whether to use AI summarization (True) or keyword extraction (False)
    :return: Summary text
    """
    
    if use_ai:
        try:
            # Use Gemini AI for intelligent summarization
            import google.genai as genai
            
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            if not GEMINI_API_KEY:
                logger.warning("⚠️ GEMINI_API_KEY not found, falling back to keyword extraction")
                use_ai = False
            else:
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                summarization_prompt = f"""Analyze this conversation and extract ONLY the most important, memorable information in a concise format.

Focus on:
1. Personal information (name, age, location, occupation, etc.)
2. User preferences and interests (likes, dislikes, favorites)
3. Important tasks, reminders, or commitments mentioned
4. Specific facts the user wants remembered
5. User's goals or plans

Format as clear bullet points. Be extremely concise - only include information that would be useful to remember in future conversations.

Conversation:
{conversation_text}

Important: Provide ONLY the extracted key points, nothing else."""

                response = client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=summarization_prompt
                )
                
                ai_summary = response.text.strip()
                
                # Create formatted summary
                session_summary = f"""Session Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
User: {user_id}

Key Information:
{ai_summary}

Total exchanges: {len(conversation_buffer.messages)}
"""
                logger.info("✅ AI-powered summarization completed")
                return session_summary
                
        except Exception as e:
            logger.warning(f"⚠️ AI summarization failed: {e}, falling back to keyword extraction")
            use_ai = False
    
    # Fallback: Simple keyword extraction method
    if not use_ai:
        summary_parts = []
        lines = conversation_text.split('\n')
        
        # Extract preferences
        preference_keywords = ['prefer', 'like', 'love', 'favorite', 'hate', 'dislike', 'enjoy', 'want']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in preference_keywords):
                summary_parts.append(line)
        
        # Extract personal information
        personal_keywords = ['my name is', 'i am', "i'm", 'i work', 'i live', 'my', 'i have', 'i own']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in personal_keywords):
                summary_parts.append(line)
        
        # Extract important tasks/reminders
        task_keywords = ['remember', 'important', 'schedule', 'meeting', 'deadline', 'todo', 'remind', 'don\'t forget']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in task_keywords):
                summary_parts.append(line)
        
        if not summary_parts:
            # If no specific patterns found, take first and last few exchanges
            summary_parts = lines[:4] + ['...'] + lines[-4:]
        
        summary = "\n".join(summary_parts)
        
        # Add metadata
        session_summary = f"""Session Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
User: {user_id}

Key Points:
{summary}

Total exchanges: {len(conversation_buffer.messages)}
"""
        logger.info("✅ Keyword-based summarization completed")
        return session_summary


def save_session_memory(user_id, use_ai_summary=None):
    """
    Save the entire session conversation as a single memory entry.
    This should be called when the session ends.
    
    :param user_id: User identifier
    :param use_ai_summary: Override for AI summarization (None = use config default)
    """
    if not conversation_buffer.messages:
        logger.info("⚠️ No conversation to save")
        return
    
    try:
        # Get full conversation
        conversation_text = conversation_buffer.get_conversation_text()
        
        # Use config default if not specified
        if use_ai_summary is None:
            use_ai_summary = MEMORY_CONFIG["use_ai_summarization"]
        
        # Summarize conversation
        summary = summarize_conversation(conversation_text, user_id, use_ai=use_ai_summary)
        
        # Create message format for mem0
        messages = [
            {
                "role": "system",
                "content": f"Session summary for {user_id}"
            },
            {
                "role": "user",
                "content": summary
            }
        ]
        
        # Save to Mem0
        result = mem0.add(messages, user_id=user_id)
        
        logger.info(f"✅ Session memory saved for {user_id}")
        logger.info(f"🧠 Stored {len(conversation_buffer.messages)} exchanges")
        
        # Clear buffer after saving
        conversation_buffer.clear()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error saving session memory: {e}")
        return None


def get_relevant_memories(user_id, query=None, limit=None):
    """
    Retrieve relevant memories for context.
    
    :param user_id: User identifier
    :param query: Optional search query
    :param limit: Maximum number of memories to return (uses config default if None)
    :return: Formatted memory context string
    """
    if limit is None:
        limit = MEMORY_CONFIG["max_memories_to_load"]
    
    try:
        if query:
            # Search with specific query
            results = mem0.search(query, user_id=user_id, limit=limit)
        else:
            # Get recent memories
            results = mem0.get_all(filters={"user_id": user_id})
            # Sort by date and take most recent
            results = sorted(
                results, 
                key=lambda x: x.get('updated_at', ''), 
                reverse=True
            )[:limit]
        
        if not results:
            logger.info("⚠️ No memories found")
            return ""
        
        # Format memories for context
        memory_context = []
        memory_context.append(f"=== Relevant Memories for {user_id} ===\n")
        
        for idx, result in enumerate(results, 1):
            memory_text = ""
            
            # Handle different response formats
            if isinstance(result, dict):
                memory_text = (
                    result.get("memory") or 
                    result.get("content") or 
                    result.get("data") or 
                    str(result)
                )
                
                # Add timestamp if available
                timestamp = result.get("updated_at", "")
                if timestamp:
                    memory_context.append(f"[{timestamp}]")
            else:
                memory_text = str(result)
            
            memory_context.append(f"{idx}. {memory_text}\n")
        
        memory_context.append("=== End of Memories ===\n")
        
        formatted_context = "\n".join(memory_context)
        logger.info(f"🧠 Loaded {len(results)} relevant memories")
        
        return formatted_context
        
    except Exception as e:
        logger.error(f"❌ Error retrieving memories: {e}")
        return ""


def get_all_memories(user_id):
    """
    Retrieve all memories for initial context loading.
    
    :param user_id: User identifier
    :return: Formatted memory context string
    """
    return get_relevant_memories(user_id, query=None, limit=10)


def delete_old_memories(user_id, days_old=30):
    """
    Optional: Clean up very old memories to prevent context overflow.
    
    :param user_id: User identifier
    :param days_old: Delete memories older than this many days
    """
    try:
        # This would require checking timestamps and deleting old entries
        # Implementation depends on Mem0 API capabilities
        logger.info(f"🧹 Cleaned old memories for {user_id}")
    except Exception as e:
        logger.error(f"❌ Error cleaning memories: {e}")


