from ably import AblyRest
from django.conf import settings
import os

# Initialize Ably client (prefer settings/env over hardcoded key)
_ABLY_API_KEY = getattr(settings, 'ABLY_API_KEY', None) or os.environ.get('ABLY_API_KEY') or 'X2wYaQ.vXSY1g:P81am9AR2FXnJX-OBBsE_5sfFWaIxgvqbayyVWliK4g'
ably = AblyRest(_ABLY_API_KEY)

def get_channel_name(user1_id, user2_id):
    """
    Generate a consistent channel name for two users
    Channel names are in format: private-chat-{minUserId}-{maxUserId}
    """
    user_ids = sorted([str(user1_id), str(user2_id)])
    return f'private-chat-{user_ids[0]}-{user_ids[1]}'

async def publish_message(channel_name, message_data):
    """
    Publish a message to an Ably channel
    """
    from asgiref.sync import sync_to_async
    channel = ably.channels.get(channel_name)
    await sync_to_async(channel.publish)('message', message_data)


def publish_message_sync(channel_name, message_data):
    """Synchronous helper to publish a message to an Ably channel.

    Use this from synchronous Django views. The underlying Ably REST
    client is synchronous, so this simply calls through.
    """
    channel = ably.channels.get(channel_name)
    # AblyRest channel.publish is synchronous
    channel.publish('message', message_data)

def generate_client_token(user_id, capabilities=None):
    """
    Generate an Ably token request for the given user and capabilities.
    This returns a token request that the frontend can use to authenticate.
    """
    if capabilities is None:
        # Default capabilities - can subscribe to private channels for their chats
        capabilities = {
            'private-chat-*': ['subscribe', 'presence']
        }
    
    # Convert capabilities dict to JSON string format that Ably expects
    import json
    capability_json = json.dumps(capabilities)
    
    try:
        # Create a token request (synchronous with AblyRest)
        token_request = ably.auth.create_token_request({
            'client_id': str(user_id),
            'capability': capability_json
        })
        
        # If token_request is a coroutine, we need to handle it differently
        import inspect
        if inspect.iscoroutine(token_request):
            # Import asyncio to run the coroutine
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            token_request = loop.run_until_complete(token_request)
        
        # Convert TokenRequest object to dict for JSON serialization
        if hasattr(token_request, '__dict__'):
            # If it's an object with attributes, convert to dict
            return {
                'keyName': getattr(token_request, 'key_name', None),
                'timestamp': getattr(token_request, 'timestamp', None),
                'nonce': getattr(token_request, 'nonce', None),
                'mac': getattr(token_request, 'mac', None),
                'capability': getattr(token_request, 'capability', capability_json),
                'clientId': str(user_id)
            }
        else:
            # Already a dict
            return token_request
    except Exception as e:
        # Fallback: generate a simple token instead
        print(f"Error generating token request: {e}")
        # Generate a simple token as fallback
        token = ably.auth.request_token({
            'client_id': str(user_id),
            'capability': capability_json
        })
        return {
            'token': token.token,
            'expires': token.expires,
            'capability': capability_json,
            'clientId': str(user_id)
        }