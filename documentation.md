# Image Generator Documentation

This project contains a Python script `generate_images.py` that uses the Google Gemini API (specifically **Imagen 4**) to generate pairs of realistic human images (one happy, one sad).

## Project Structure

- `generate_images.py`: The main script using `google-genai` SDK.
- `requirements.txt`: List of Python dependencies.
- `.env`: Configuration file for API keys.
- `images/`: Directory where generated images are saved.

## Setup Instructions

1.  **Install Python**: Ensure you have Python installed (3.9+ recommended).
    ```bash
    python --version
    ```

2.  **Install Dependencies**:
    Since this project uses modern Google Gen AI SDKs, it is recommended to install dependencies in user scope to avoid system conflicts:
    ```bash
    pip install --user -r requirements.txt
    ```
    *Note: On some systems (like WSL/Ubuntu), you might need `--break-system-packages` if not using a virtual environment.*
    ```bash
    pip install --user --break-system-packages -r requirements.txt
    ```

3.  **Configure API Key**:
    - Open the `.env` file in the root directory.
    - Add your Gemini API key:
      ```env
      GEMINI_API_KEY=your_actual_api_key_here
      ```
    - You can get an API key from [Google AI Studio](https://aistudio.google.com/).

## Usage

Run the script using Python:

```bash
python3 generate_images.py
```

## Functionality

The script will:
1.  Connect to the Gemini API using `google-genai` SDK.
2.  Use the **Imagen 4** model (`models/imagen-4.0-generate-001`) for state-of-the-art realistic image generation.
3.  Create an `images/` directory if it doesn't exist.
4.  Loop 10 times to generate 10 pairs of images.
5.  For each pair, it:
    - **Generates a Consistent Scene**: Selects a uniform background (e.g., "busy city street", "quiet park") and lighting condition for both images to ensure valid comparison.
    - **Maintains Identity**: Uses the same age, gender, and features for both the Happy and Sad versions.
    - **Varies Expression**: Changes only the facial expression and emotional body language.
    - Saves images as `{i}_sad.png` and `{i}_happy.png`.

## Prompt Engineering for Realism

The script uses advanced prompt engineering to ensure high-fidelity results:
- **Shared Context**: Background and lighting are locked per pair.
- **Hyper-Realism**: Keywords like "visible pores", "vellus hair", "raw photo", "Sony A7R V" are used to enforce photorealism.
- **Logical Consistency**: Features are gender-appropriate.
- **1:1 Identity Match**: The script ensures the person is identical in both images by generating the "Happy" version first, then using it as an *input* to generate the "Sad" version via image editing.

### Models
The script supports two generation modes:
1.  **Nano Banana (`gemini-2.5-flash-image`)**: Uses `generate_content` to produce images. This model typically has a separate, higher quota than Imagen 4. *This is the default.*
2.  **Imagen 4 (`imagen-4.0-generate-001`)**: Uses `generate_images`. Offers premium realism ("Sony A7R V" style) but has stricter daily quotas.

To switch back to Imagen 4, edit `generate_images.py` and uncomment the corresponding `model_name` line.

## Troubleshooting

- **Error: GEMINI_API_KEY not found**: Make sure you modified the `.env` file and saved it.
- **404 NOT_FOUND**: Ensure your API key has access to `models/imagen-4.0-generate-001`.
- **400 INVALID_ARGUMENT (Safety)**: The script is configured to use `block_low_and_above`.
- **429 RESOURCE_EXHAUSTED**: You have exceeded your daily API quota for image generation (limit: 70 requests/day for paid tier). Wait until the next day or check your billing plan.
