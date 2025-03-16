import asyncio
from edge_tts import VoicesManager

async def list_voices():
    # Create a VoicesManager instance
    voices_manager = await VoicesManager.create()
    
    # Access the list of voices
    voices = voices_manager.voices
    
    # Print details of each voice
    for voice in voices:
        print(f"Name: {voice['Name']}, Gender: {voice['Gender']}, Locale: {voice['Locale']}")

# Run the async function
asyncio.run(list_voices())