<p align="center">English | <a href="README_zh.md">中文</a><p>

# AI Code Context Helper

## 📝 Introduction

AI Code Context Helper is a lightweight desktop application designed for developers collaborating with AI assistants. It provides a visual representation of project structures and enables quick, selective export of file paths and code content to the clipboard, streamlining code communication with ChatGPT, Claude, and other AI assistants.

As a supplementary tool, it doesn't aim to replace existing editors or IDEs but focuses specifically on solving the code context transfer challenge in AI programming collaboration. Compared to integrated AI code editors, it offers advantages in simplicity, low learning curve, independence from specific AI services, and minimal resource usage, integrating seamlessly with various development environments.

![Application Overview](./_images/app_overview.png)

<!-- 👆 Main interface screenshot -->

## ✨ Key Features

### Intelligent File Management
- **Directory Tree Visualization**: Display project file structure in tree view
- **File Type Recognition**: Automatically detect text file encodings and distinguish between text and binary files
- **Advanced Filtering**: Support for regex filtering and directory depth limitation for handling large projects

### Flexible Selection and Export
- **Multi-selection Support**: Select individual files, multiple files, or entire directories with subdirectories
- **Batch Export**: Export paths, code, or both for selected content
- **Context Menu**: Multiple copy options for different development scenarios

### Customization and Ease of Use
- **Multilingual Support**: Switch between English and Chinese interfaces
- **Output Format Customization**: Configure prefix and suffix formats for code and paths
- **Lightweight Implementation**: Low resource consumption, quick startup, seamlessly integrates with existing development workflows

## 💡 Usage Tips

### Best Practice: Combining Project Structure with Code Content

For better AI comprehension of your project, follow these steps:

1. **First Share Project Structure**:
   - Select the root directory and use the "Copy Tree" function
   - Paste the directory tree to the AI to provide overall project architecture

2. **Then Share Key Files**:
   - Select relevant files based on your requirements (multiple files or directories)
   - Use "Copy Path and Code" to provide all necessary files at once

3. **Reference File Paths in Requirements**:
   - Example: "Please modify the `authenticate` method in `models/user.py` to add two-factor authentication"
   - Clear path references help AI locate relevant code accurately

### Module-Level Modifications

When modifying an entire functional module:

1. Select the module directory (e.g., `authentication/` folder)
2. Right-click and choose "Copy Path and Code" to include all files in the directory
3. Describe to the AI: "Please analyze this authentication module and suggest improvements"

> For codebases under 5,000 lines, you can copy all code directly to AI assistants like Claude or ChatGPT for code review and get complete modified code. This is essentially pair programming with AI - efficiency improves with your coding and requirements description skills.

## 📸 Screenshots

### Context Menu

![Right-click Menu](./_images/context_menu.png)

<!-- 👆 Right-click menu screenshot -->

## 🔧 Installation and Usage

### Download and Install

1. Download the latest version from the [Releases page](https://github.com/sansan0/ai-code-context-helper/releases)
2. Extract the files to any location
3. Run `AI Code Context Helper.exe` to launch the application

### How to Use

1. Click "Browse..." to select your project root directory
2. Check the files or folders you want to share in the directory tree
3. Right-click and select "Copy Path and Code" (or other copy options)
4. Paste the copied content into your AI assistant (ChatGPT, Claude, etc.)
5. Ask questions or request code modifications based on the provided context

## ⚙️ Configuration Options

### Interface Options

- **Show Hidden Files**: Toggle display of hidden files and folders
- **Show Files/Show Folders**: Control what appears in the tree view
- **Preserve Tree State**: Maintain expansion/collapse state when resetting
- **Use Relative Path**: Use paths relative to the root directory instead of absolute paths
- **Max Depth**: Limit the display depth of the directory tree
- **File Filter**: Filter displayed files using regular expressions

## 🛠️ Building from Source

### Requirements

- Python 3.9+
- Poetry package manager

### Install Dependencies

```bash
git clone https://github.com/sansan0/ai-code-context-helper.git
cd ai-code-context-helper
poetry install
```

### Build Executable

```bash
poetry run python -m cx_Freeze build
```

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.