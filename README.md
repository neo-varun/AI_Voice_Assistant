# AI Voice Assistant

## Overview
This project is an **AI Voice Assistant** built using **Flask**, **OpenAI GPT**, and various **Speech-to-Text/Text-to-Speech services**. It allows users to have **natural conversations in multiple languages** with an AI assistant through a **web interface**.

The application supports **multiple speech recognition providers**, handles **conversation context**, and offers **voice customization options** for a personalized experience.

## Features
- **Multiple Speech Recognition Providers** – Deepgram, Google Cloud, and AssemblyAI
- **Multilingual Support** – English, Tamil, Kannada, Telugu, Malayalam, and Hindi
- **Conversation History & Summarization** – Maintains context for more relevant responses
- **Voice Customization** – Different language options and voice genders
- **Responsive Web Interface** – Clean and intuitive design for easy interaction

## Prerequisites

### API Keys
Before running the application, you must have API keys for the following services:

- **OpenAI API** – Get your API key from [OpenAI](https://platform.openai.com/api-keys)
- **Google Cloud** – Set up a project and enable Speech-to-Text and Text-to-Speech APIs
- **Deepgram** – Register for an API key at [Deepgram](https://deepgram.com/)
- **AssemblyAI** – Get your API key from [AssemblyAI](https://www.assemblyai.com/)

### Environment Variables
You'll need to set up the following environment variables:
- `OPENAI_API_KEY` – Your OpenAI API key
- `GOOGLE_APPLICATION_CREDENTIALS` – Path to your Google Cloud credentials JSON file
- `DEEPGRAM_API_KEY` – Your Deepgram API key
- `ASSEMBLY_API_KEY` – Your AssemblyAI API key

## Installation & Setup

### Create a Virtual Environment (Recommended)
It is recommended to create a virtual environment to manage dependencies:
```bash
python -m venv venv
```
Activate the virtual environment:
- **Windows:**  
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**  
  ```bash
  source venv/bin/activate
  ```

### Install Dependencies
Ensure you have **Python 3.x** installed, then install the required packages:
```bash
pip install -r requirements.txt
```

### Run the Flask App
Navigate to the project directory and run:
```bash
python app.py
```
The application will be available at `http://127.0.0.1:8000/`.

## How the Program Works

### Web Interface
- The application presents a **microphone button** for recording user speech.
- Users can customize their experience through **language options**:
  - Select a **speech recognition model** (Deepgram, Google Cloud, or AssemblyAI)
  - Choose the **speech recognition language**
  - Select a **text-to-speech voice language**
  - Choose the **voice gender** (Male or Female)

### Voice Processing Pipeline
1. **Speech Capture** – User's voice is recorded through the browser
2. **Speech-to-Text** – Audio is sent to the selected provider for transcription
3. **Language Processing** – Transcribed text is processed by OpenAI's GPT model
4. **Response Generation** – The AI formulates a natural, contextual response
5. **Text-to-Speech** – Response is converted to audio using Google Cloud TTS
6. **Audio Playback** – The assistant's voice response is played to the user

### Conversation Management
- The application keeps track of conversation history using a **session ID**
- Previous exchanges are **summarized** to maintain context without exceeding token limits
- This allows the assistant to refer to earlier parts of the conversation naturally

## Technologies Used
- **Flask** (Backend Web Framework)
- **OpenAI GPT Models** (Natural Language Processing)
- **Speech Recognition Services**:
  - Deepgram (Nova-2 and Nova-3 models)
  - Google Cloud Speech-to-Text
  - AssemblyAI (Best and Nano models)
- **Google Cloud Text-to-Speech** (Voice Synthesis)
- **HTML/CSS/JavaScript** (Frontend)

## License
This project is licensed under the **MIT License**.

## Author
Developed by **Varun**. Feel free to connect with me on:
- **Email:** darklususnaturae@gmail.com 