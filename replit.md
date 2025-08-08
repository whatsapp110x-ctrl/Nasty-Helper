# Telegram Link Sharing Bot

## Overview

This is a simple Telegram bot built with Python that provides basic command handling functionality and link sharing capabilities. The bot is designed to respond to user commands, provide help information, and share website links. It uses the python-telegram-bot library for Telegram API integration and is configured for deployment on cloud platforms like Render.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture
- **Event-driven command handling**: Uses telegram.ext framework with separate handlers for different command types
- **Modular design**: Core bot logic separated into dedicated TelegramBot class with clean separation of concerns
- **Asynchronous processing**: Built on async/await pattern for handling Telegram API calls efficiently

### Application Structure
- **Single-file bot logic**: Core functionality contained in `bot.py` with clear handler registration pattern
- **Configuration management**: Centralized configuration in `config.py` using environment variables for sensitive data
- **Simple entry point**: `main.py` serves as the application launcher with basic error handling and logging setup

### Command System
- **Handler registration**: Commands registered through telegram.ext's CommandHandler system
- **Message filtering**: Separate handlers for commands vs. regular text messages
- **Response patterns**: Structured response messages with consistent formatting and emoji usage

### Configuration Management
- **Environment-based configuration**: Bot token and deployment settings loaded from environment variables
- **Centralized constants**: All bot messages, commands, and settings defined in single configuration file
- **Deployment flexibility**: Configuration supports multiple deployment environments through environment variable overrides

### Error Handling and Logging
- **Structured logging**: Python logging module with timestamps and log levels
- **Graceful error handling**: Try-catch blocks around critical operations with user-friendly error messages
- **Configuration validation**: Token presence validation before bot startup

## External Dependencies

### Core Dependencies
- **python-telegram-bot**: Official Telegram Bot API wrapper for Python, handles all Telegram communication
- **Python standard library**: Uses os, logging, and other built-in modules for basic functionality

### Deployment Infrastructure
- **Cloud platform deployment**: Configured for platforms like Render with HOST and PORT environment variables
- **Environment variable management**: Relies on platform-provided environment variable injection for configuration

### Telegram API Integration
- **Telegram Bot API**: Direct integration with Telegram's bot platform through official Python library
- **Webhook/polling support**: Architecture supports both polling and webhook modes for message handling