"""
Minimal test handler for Vercel
"""

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"message": "Hello from Vercel!", "status": "working"}'
    }
