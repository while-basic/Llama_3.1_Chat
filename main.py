import asyncio
import aiohttp
from groq import AsyncGroq
import os
from colorama import Fore, Style, init
from dotenv import load_dotenv

load_dotenv()
init()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def get_ai_response(messages):
    try:
        completion = await client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )
        print(f"{Fore.GREEN}AI: ", end="", flush=True)
        response = ""
        async for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            response += content
        print(Style.RESET_ALL)
        return response
    except aiohttp.ClientError as e:
        print(f"{Fore.RED}Error: Network issue - {str(e)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    return None

async def process_command(command, messages):
    if command == "/clear":
        messages = messages[:1]  # Keep only the system message
        print(f"{Fore.YELLOW}Conversation history cleared.{Style.RESET_ALL}")
    elif command == "/save":
        with open("conversation.txt", "w") as f:
            for msg in messages:
                f.write(f"{msg['role']}: {msg['content']}\n")
        print(f"{Fore.YELLOW}Conversation saved to conversation.txt{Style.RESET_ALL}")
    elif command == "/help":
        print(f"{Fore.YELLOW}Available commands:{Style.RESET_ALL}")
        print("/clear - Clear conversation history")
        print("/save - Save conversation to file")
        print("/help - Show this help message")
    else:
        print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")
    return messages

async def chat():
    default_system_prompt = "You are a helpful AI assistant. Provide concise and accurate responses."
    system_prompt = input(f"{Fore.YELLOW}Enter a system prompt (or press Enter for default): {Style.RESET_ALL}")
    if not system_prompt:
        system_prompt = default_system_prompt
    
    messages = [{"role": "system", "content": system_prompt}]
    print(f"{Fore.YELLOW}Welcome to the AI chat! Type 'exit' to end the conversation.{Style.RESET_ALL}\n")
    
    while True:
        user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}")
        if user_input.lower() == 'exit':
            break
        if user_input.startswith("/"):
            messages = await process_command(user_input, messages)
            continue
        
        messages.append({"role": "user", "content": user_input})
        ai_response = await get_ai_response(messages)
        if ai_response:
            messages.append({"role": "assistant", "content": ai_response})
        print()
    
    print(f"\n{Fore.YELLOW}Thank you for chatting! Goodbye!{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(chat())