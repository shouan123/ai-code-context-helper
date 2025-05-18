<p align="center">English | <a href="README.md">中文</a><p>

## 📝 Introduction

AI Code Context Helper is a lightweight desktop application designed for anyone who needs to understand, learn, or develop code. Whether you're a programming beginner, professional developer, or educator, it helps you easily extract code context and communicate efficiently with AI assistants. Through visual project structure displays and one-click code export, it makes understanding complex code, getting AI programming suggestions, and conducting code reviews unprecedentedly simple. This powerful yet simple tool accelerates the learning curve for beginners while improving productivity for professional developers, regardless of whether you're learning code, developing new features, or seeking improvement suggestions.

<p align="center">
  <img src="./_images/app.gif" width="50%" alt="Animation">
</p>

## 👥 Target Users

- **Programming Beginners**: Understand open-source project structures and code logic through AI, accelerating your learning curve
- **Software Developers**: Seamlessly integrate AI programming assistants into existing workflows to improve development efficiency
- **Code Reviewers**: Quickly extract project module code and leverage AI for quality reviews and optimization suggestions
- **Technical Educators**: Explain code structures and implementation details more effectively as teaching aids
- **Open Source Contributors**: Rapidly familiarize yourself with new project codebases, lowering barriers to contribution

## 🎯 Key Application Scenarios

This tool allows you to easily pass code context to AI assistants for:

- **Code Learning**: Understanding complex project structures and mechanisms, improving learning efficiency
- **Development Assistance**: Getting more accurate code modification and feature implementation suggestions
- **Code Reviews**: Conducting automated quality checks and performance optimization analysis
- **Refactoring Guidance**: Receiving code improvement suggestions based on complete context
- **Problem Diagnosis**: Helping AI precisely locate issues by providing the complete environment

All features run locally without internet connection, ensuring the privacy and security of your code.

## 💡 Core Use Cases

### 1. Code Learning & Analysis

Easily let AI help you understand how complex codebases work:

1. **Select Target Project Directory**: Open the project you want to analyze
2. **Copy Complete Project Structure**: Use the "Copy Directory Tree" function to help AI understand the overall architecture
3. **Provide Core Code Files**: Select key files and use "Copy Path and Code" to provide all code at once
4. **Ask AI for Analysis**: Request AI to analyze code structure, explain how it works, or suggest a learning path

> Understanding a complex open-source project used to take days. Now you can get an overview and analysis of key parts from AI, greatly improving learning efficiency!

### 2. Code Modification & Development

Get AI programming assistance without disrupting your existing workflow:

1. **Locate Modules Needing Changes**: Find relevant files through the visual tree structure
2. **Export Related Code Context**: Select multiple related files simultaneously (e.g., models, controllers, and views)
3. **Describe Modification Requirements**: Clearly explain to AI what functionality you want to implement or what problem needs fixing
4. **Get Complete Implementation Plan**: AI will provide accurate code modification suggestions based on the complete context

> Compared to single-file editor integrations, this approach provides more complete project context, resulting in more accurate and actionable code suggestions

### 3. Code Review & Refactoring

Let AI become your code review assistant:

1. **Select Module for Review**: Box-select all files in a functional module
2. **Copy All Related Code with One Click**: Include complete implementation details and file paths
3. **Request AI Review**: Get feedback on code quality, potential issues, and improvement suggestions
4. **Implement Refactoring Suggestions**: Apply optimization solutions provided by AI

> If the total code is under 5,000 lines, you can copy it all to mainstream AI assistants for comprehensive analysis, faster and more thorough than traditional code reviews

### Local Execution, Privacy Protection

- **Completely Offline Operation**: The software runs locally, requires no internet connection, and never uploads any code
- **Privacy Protection**: Your code only leaves your computer when you actively copy it
- **Compatible with Any AI Assistant**: You're free to choose which AI service to use, with complete control over code sharing

<p align="center">
  <img src="./_images/app_overview.png" width="50%" alt="Application overview screenshot">
</p>

## ✨ Key Features

### Intelligent File Management

- **Directory Tree Visualization**: Tree view displays project file structure
- **File Type Recognition**: Automatically detects text file encoding, distinguishes between text and binary files
- **Advanced Filtering**: Supports regular expression filtering, .gitignore rule application, and directory depth limits for handling large projects

### Flexible Selection & Export

- **Multi-selection Support**: Select single files, multiple files, or entire directories and their subdirectories
- **Mouse Box Selection Mode**: Select/deselect multiple files at once by dragging the mouse
- **Batch Export**: Export paths, code, or both for selected content
- **Context Menu**: Provides multiple copy options for different development scenarios

### Integration & Convenience

- **System Tray Integration**: Minimize to system tray, available anytime without occupying desktop space
- **Global Hotkey**: Press Ctrl+2 from any application to show/hide the application window
- **Window Always-on-Top Option**: Keep the window above other applications for convenience
- **File System Integration**: Open folders in file explorer or launch command-line terminals directly from the context menu

### Customization & Ease of Use

- **Multi-language Support**: Switch between English and Chinese
- **Output Format Customization**: Configure prefixes and suffixes for code and paths
- **Advanced Options Toggle**: Hide/show advanced settings to maximize directory tree display space
- **Lightweight Implementation**: Low resource usage, quick startup, seamlessly integrates into existing development workflows

## 🔑 Shortcuts & Special Functions

- **Ctrl+C**: Copy paths and code of selected files
- **Ctrl+B**: Copy filenames of selected files
- **Ctrl+F**: Open selected folder in file explorer
- **Ctrl+T**: Open command-line terminal in selected folder
- **Ctrl+2**: Global hotkey to show/hide the application from anywhere
- **Tree State Preservation**: The application remembers expansion state of each project directory between sessions

## 📸 Application Screenshots

### Directory Tree Menu

<p align="center">
  <img src="./_images/context_menu.png" width="60%" alt="Right-click menu">
</p>

## 🔧 Installation & Usage

### Download & Install

1. Download the latest version from the [Releases page](https://github.com/sansan0/ai-code-context-helper/releases)
2. Extract the downloaded file to any location
3. Run `AI Code Context Helper.exe` to launch the application

### How to Use

1. Click "Browse..." to select your project root directory
2. Check the files or folders you want to share in the directory tree
3. Right-click and select "Copy Path and Code" (or other copy options)
4. Paste the copied content into an AI assistant (like ChatGPT, Claude, etc.)
5. Ask questions or request code modification suggestions based on the provided code context

## ⚙️ Configuration Options

### Interface Options

- **Show Hidden Files**: Whether to display hidden files and folders
- **Show Files/Show Folders**: Control what appears in the tree view
- **Use Relative Path**: Use paths relative to the root directory instead of absolute paths
- **Filter by .gitignore**: Apply rules from the project's .gitignore file
- **Mouse Box Selection Mode**: Enable drag selection for batch operations
- **Maximum Depth**: Limit the display depth of the directory tree
- **File Filter**: Filter displayed files using regular expressions
- **Keep on Top**: Keep the window above all other applications
- **Advanced Options Toggle**: Hide/show advanced settings to maximize tree display space

## 🛠️ Building from Source

### Requirements

- Python 3.9+
- Poetry package manager

### Installing Dependencies

```bash
git clone https://github.com/sansan0/ai-code-context-helper.git
cd ai-code-context-helper
poetry install
```

### Building the Executable

```bash
poetry run python -m cx_Freeze build
```

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details
