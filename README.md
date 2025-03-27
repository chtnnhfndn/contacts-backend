# Contacts Backend

## Overview

Privacy-first social networking platform backend using FastAPI and Supabase.

## Features

- User registration and authentication
- Multiple profile support
- Secure NFC profile sharing
- Comprehensive error handling
- Async database operations

## Prerequisites

- Python 3.10+
- Poetry
- Supabase Account

## Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   poetry install
   ```

3. Set up environment variables:

   ```md
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_key
   ```

## Running the Application

```bash
poetry run uvicorn app.main:app --reload
```

## Testing

```bash
poetry run pytest
```

## Security Considerations

- Uses Supabase for authentication
- Implements comprehensive error handling
- Token-based authentication
- NFC profile sharing with secure tokens

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
