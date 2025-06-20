# Project Structure: logonico

``````
[ROOT] logonico
|-- [DIR] cache
|   |-- [JSON]replicate_versions.json
|-- [DIR] config
|   |-- [JSON]prompts.json
|-- [DIR] logonico-ui
|   |-- [DIR] public
|   |   |-- [FILE]favicon.ico
|   |   |-- [HTML]index.html
|   |   |-- [FILE]logo192.png
|   |   |-- [FILE]logo512.png
|   |   |-- [JSON]manifest.json
|   |   |-- [TXT] robots.txt
|   |-- [DIR] src
|   |   |-- [DIR] components
|   |   |   |-- [DIR] common
|   |   |   |   |-- [JS]  ActionButton.js
|   |   |   |   |-- [JS]  FilterButton.js
|   |   |   |   |-- [JS]  ImageCard.js
|   |   |   |   |-- [JS]  LoadingSpinner.js
|   |   |   |   |-- [JS]  ProgressBar.js
|   |   |   |   |-- [JS]  StatusBadge.js
|   |   |   |-- [DIR] Footer
|   |   |   |   |-- [JS]  Footer.js
|   |   |   |-- [DIR] Gallery
|   |   |   |   |-- [JS]  Gallery.js
|   |   |   |   |-- [JS]  ImageGrid.js
|   |   |   |   |-- [JS]  LogEntry.js
|   |   |   |   |-- [JS]  ProviderDots.js
|   |   |   |   |-- [JS]  ResizeHandle.js
|   |   |   |   |-- [JS]  SelectionActions.js
|   |   |   |-- [DIR] Header
|   |   |   |   |-- [JS]  Header.js
|   |   |   |-- [DIR] Layout
|   |   |   |   |-- [JS]  AppLayout.js
|   |   |   |   |-- [JS]  PanelContainer.js
|   |   |   |-- [DIR] SelectionPanel
|   |   |   |   |-- [JS]  SelectionPanel.js
|   |   |   |-- [DIR] Sidebar
|   |   |   |   |-- [JS]  Sidebar.js
|   |   |-- [DIR] hooks
|   |   |   |-- [JS]  useAppState.js
|   |   |   |-- [JS]  useImages.js
|   |   |   |-- [JS]  useLogs.js
|   |   |   |-- [JS]  useResizePanel.js
|   |   |   |-- [JS]  useStats.js
|   |   |   |-- [JS]  useTheme.js
|   |   |-- [DIR] services
|   |   |   |-- [JS]  apiService.js
|   |   |   |-- [JS]  fileUtils.js
|   |   |   |-- [JS]  imageParser.js
|   |   |   |-- [JS]  themeService.js
|   |   |-- [DIR] (empty) styles
|   |   |-- [DIR] (empty) types
|   |   |-- [DIR] (empty) utils
|   |   |-- [CSS] App.css
|   |   |-- [JS]  App.js
|   |   |-- [JS]  App.test.js
|   |   |-- [CSS] index.css
|   |   |-- [JS]  index.js
|   |   |-- [FILE]logo.svg
|   |   |-- [JS]  reportWebVitals.js
|   |   |-- [JS]  setupTests.js
|   |-- [FILE].gitignore
|   |-- [JSON]package.json
|   |-- [JSON]package-lock.json
|   |-- [MD]  README.md
|-- [DIR] src
|   |-- [DIR] core
|   |   |-- [PY]  (empty) __init__.py
|   |   |-- [PY]  config.py
|   |   |-- [PY]  models.py
|   |   |-- [PY]  pipeline.py
|   |-- [DIR] generators
|   |   |-- [PY]  (empty) __init__.py
|   |   |-- [PY]  base.py
|   |   |-- [PY]  fal_ai.py
|   |   |-- [PY]  openai.py
|   |   |-- [PY]  replicate.py
|   |   |-- [PY]  together_ai.py
|   |-- [DIR] processors
|   |   |-- [PY]  (empty) __init__.py
|   |   |-- [PY]  background_remover.py
|   |   |-- [PY]  ico_converter.py
|   |   |-- [PY]  image_optimizer.py
|   |-- [DIR] utils
|   |   |-- [PY]  (empty) __init__.py
|   |   |-- [PY]  api_utils.py
|   |   |-- [PY]  file_utils.py
|   |   |-- [PY]  logging_utils.py
|   |   |-- [PY]  naming.py
|   |-- [PY]  (empty) __init__.py
|-- [DIR] templates
|   |-- [HTML]index.html
|-- [DIR] (empty) tests
|-- [FILE].gitignore
|-- [PY]  app.py
|-- [PY]  main.py
|-- [MD]  modularization.md
|-- [MD]  project_review_assessment.md
|-- [MD]  README.md
|-- [TXT] requirements.txt
|-- [PY]  setup.py
|-- [SCRIPT]setup_windows.bat
``````

## Summary

- **Total Items Displayed**: 103
- **Project Root**: `C:\Projects\logonico`
