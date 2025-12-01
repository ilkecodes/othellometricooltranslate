---
title: Vapi Gemma API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Vapi Gemma Sales API

Custom LLM API for Vapi using fine-tuned Gemma model for sales conversations.

## Model

- Base: `google/gemma-1.1-2b-it`
- Adapter: `ilkeileri/gemma-sales-comprehensive`
- Method: LoRA fine-tuning

## API Endpoint

```
POST /chat/completions
```

### Request Format

```json
{
  "messages": [
    {"role": "user", "content": "How do I handle a price objection?"}
  ]
}
```

### Response Format

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Your response here..."
    }
  }]
}
```

## Usage with Vapi

Configure in Vapi Dashboard:
- Custom LLM URL: `https://ilkeileri-vapi-gemma-api.hf.space/chat/completions`
- Method: POST
- Content-Type: application/json
