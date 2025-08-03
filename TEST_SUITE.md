# 2DO Test Suite Documentation

## Overview

This document describes the comprehensive test suite for the 2DO application, which includes dummy tests for all components and verification systems to ensure proper setup.

## Test Structure

### Core Test Files

1. **`tests/test_basic.py`** (Original)
   - 9 fundamental tests covering core functionality
   - Todo management, tech stack detection, configuration, markdown parsing
   - GitHub integration and branch name sanitization

2. **`tests/test_setup_verification.py`** (New)
   - 13 tests for setup verification and configuration validation
   - API key configuration testing
   - Setup completeness checking
   - Configuration migration and persistence
   - Setup guidance system testing

3. **`tests/test_cli_integration.py`** (New)
   - CLI command testing and user workflow validation
   - Setup command flow testing
   - Interactive session testing
   - Error handling for CLI operations

4. **`tests/test_comprehensive.py`** (New)
   - Extensive component testing with edge cases
   - Todo manager comprehensive testing
   - Tech stack detector comprehensive testing
   - AI router testing with mocked components
   - Markdown parser edge case testing
   - Error handling across all components

5. **`tests/test_interactive_guidance.py`** (New)
   - Interactive setup guidance system testing
   - User workflow testing for setup scenarios
   - Edge case handling in setup guidance
   - Configuration validation and progress tracking

## Test Features

### Setup Verification

The test suite includes comprehensive setup verification that:

- **Detects missing components**: Identifies which API keys or configurations are missing
- **Tracks setup progress**: Calculates completion percentage (0-100%)
- **Guides users interactively**: Provides step-by-step setup assistance
- **Validates configuration**: Ensures all components are properly configured

### Dummy Testing

All major components have dummy tests that:

- **Mock external dependencies**: Uses unittest.mock to avoid real API calls
- **Test edge cases**: Covers error conditions and unusual inputs
- **Validate data flow**: Ensures proper data handling throughout the application
- **Check error handling**: Verifies graceful handling of failures

### Interactive Setup Guidance

The setup guidance system (`twodo/setup_guide.py`) provides:

- **Real-time status checking**: Displays current setup status in formatted tables
- **Interactive configuration**: Guides users through missing setup steps
- **Progress visualization**: Shows completion percentage and missing components
- **Connectivity testing**: Validates configured services
- **Local vs global detection**: Handles project-specific vs global configurations

## Test Runner

### Command Line Usage

```bash
# Run all tests with detailed reporting
python test_runner.py

# Run quick tests only
python test_runner.py --quick

# Run setup verification only
python test_runner.py --setup
```

### Features

- **Comprehensive reporting**: Detailed test results with failure analysis
- **Progress tracking**: Real-time test execution progress
- **Multiple test suites**: Organizes tests by category (basic, setup, CLI, comprehensive)
- **Integration testing**: Tests module imports and system connectivity
- **Error analysis**: Detailed failure reporting with actionable information

## CLI Integration

### New Commands

- **`2do verify`**: Comprehensive setup verification and guidance
  ```bash
  # Verify current directory setup
  2do verify
  
  # Verify specific project
  2do verify --project /path/to/project
  ```

### Workflow Testing

The test suite validates complete user workflows:

1. **Initial Setup**: From fresh installation to fully configured
2. **Partial Setup**: Handling incomplete configurations
3. **Project Detection**: Git repository vs. global configuration
4. **Error Recovery**: Handling setup failures and retries

## Setup Status Detection

### Configuration Completeness

The system tracks configuration across three main components:

1. **OpenAI API Key**: For GPT models
2. **Anthropic API Key**: For Claude models  
3. **GitHub Token**: For repository integration

### Progress Calculation

- **0%**: No components configured
- **33%**: One component configured
- **67%**: Two components configured
- **100%**: All components configured (fully ready)

### Status Reporting

```
2DO Setup Status
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component          ┃ Status            ┃ Details                                   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Configuration File │ ✅ Exists         │ Located at: ~/.2do/config.yaml            │
│ OpenAI API Key     │ ❌ Not configured │ Required for GPT models                   │
│ Anthropic API Key  │ ❌ Not configured │ Required for Claude models                │
│ GitHub Token       │ ✅ Configured     │ Required for GitHub integration           │
│ Memory System      │ ✅ Enabled        │ Tech stack memory files                   │
│ Parallel Tasks     │ ✅ 5 tasks        │ Max concurrent processing                 │
└────────────────────┴───────────────────┴───────────────────────────────────────────┘
```

## Test Coverage

### Component Coverage

- **Configuration Management**: 15+ tests
- **Todo Management**: 20+ tests  
- **Tech Stack Detection**: 10+ tests
- **CLI Integration**: 12+ tests
- **Setup Guidance**: 15+ tests
- **Error Handling**: 8+ tests

### Total Test Count

- **Original tests**: 9
- **New tests**: 50+
- **Total**: 60+ tests covering all major functionality

## Running Tests

### Prerequisites

```bash
# Install dependencies
pip install -e .
pip install pytest
```

### Basic Testing

```bash
# Run all original tests
python -m pytest tests/test_basic.py -v

# Run setup verification tests
python -m pytest tests/test_setup_verification.py -v

# Run CLI integration tests
python -m pytest tests/test_cli_integration.py -v
```

### Advanced Testing

```bash
# Run comprehensive test suite
python test_runner.py

# Quick functionality check
python test_runner.py --quick

# Setup system verification
python test_runner.py --setup
```

## Continuous Integration

The test suite is designed for CI/CD environments:

- **Exit codes**: Proper exit codes for automated testing
- **Verbose output**: Detailed reporting for debugging
- **Isolated testing**: Each test uses fresh temporary directories
- **Mock external services**: No real API calls required
- **Cross-platform compatibility**: Works on Linux, macOS, and Windows

## Future Enhancements

- **Performance benchmarking**: Add timing tests for critical operations
- **Integration with GitHub Actions**: Automated testing on commits
- **Test coverage reporting**: Measure and track code coverage
- **Stress testing**: Test with large datasets and high concurrency
- **Security testing**: Validate API key handling and data protection