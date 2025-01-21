## Table of Contents 

- [Introduction](#introduction)
    - [PDF Data Extractor](#pdf-data-extractor)
    - [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Supported Formats](#pdf-format-support)
- [Limitations](#known-limitations)
- [Contributing](#contributing)



## Introduction

### PDF Data Extractor

A simple web application that automatically extracts personal information (Name, Phone Number, Address) from PDF documents and populates a web form. The system uses Python for PDF processing, Node.js for the API server, and React for the frontend interface.


### Features

- PDF text extraction and parsing
- Automatic detection of personal information
- Real-time form population
- RESTful API endpoints
- Web-based interface
- Support for various PDF formats
- Error handling and validation


## Tech Stack

### Backend 

- Node.js
- Python 
- pdfplumber 

### Frontend 

- React 
- Tailwind CSS


## Prerequisites 

Before running this project, make sure you have:

- [Node.js](https://nodejs.org/) installed on your system
- [Python](https://www.python.org/)
- [npm](https://www.npmjs.com/)


## Installation 

1. Clone the repository: 

    ```
    git clone https://github.com/raghav-97/pdf-extractor.git
    cd pdf-extractor
    ```

2. Install Frontend Dependencies: 
    ```
    npm install
    ```

3. Navigate to backend folder and install backend Dependencies:
    ``` 
    cd backend
    npm install
    ```
4. Install Python Dependencies 
    ```
    cd backend/python
    pip install -r requirements.txt
    ```

## Usage 

1. Start the backend server: 
    Navigate to backend folder
    ```
    cd backend                  // run this in \pdf-extractor\backend directory
    node server.js
    ```

2. Start the frontend Development server: 
    ``` 
    cd ..                       // make sure you are in \pdf-extractor directory 
    npm run dev
    ```


## Project Structure 

Your project structure should look like this: 

    
    pdf-extractor/
    ├── backend/
    │   ├── node_modules/
    │   ├── python/
    │   │   ├── pdf_parser.py
    │   │   └── requirements.txt
    │   ├── uploads/          # For storing uploaded PDFs
    │   ├── package.json
    │   ├── package-lock.json
    │   └── server.js
    ├── node_modules/
    ├── public/
    ├── src/
    ├── .gitignore
    ├── eslint.config.js
    ├── index.html
    ├── package.json
    ├── postcss.config.js
    ├── README.md
    ├── tailwind.config.js
    └── vite.config.js
    


## PDF Format Support

The application can extract information from PDFs that:

Contain searchable text (not scanned images)
Have information labeled with common patterns:
- "Name:"
- "Phone:"
- "Address:"


## Known Limitations

 ### Cannot process:

 - Password-protected PDFs
 - Scanned PDFs without OCR
 - Image-only PDFs


 ### Requires specific label formats:

 - Information should be preceded by labels (e.g., "Name:", "Phone:", "Address:")
 - Text should be in a readable format


## Contributing

- Fork the repository

- Create a feature branch: 
    ```
    git checkout -b feature/my-feature
    ```

- Commit changes: 
    ```
    git commit -am 'Add new feature'
    ```
- Push to branch: 
    ```
    git push origin feature/my-feature
    ```

- Submit a Pull Request
