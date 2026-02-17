import os
import random
import time
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

def generate_pair_context():
    """Generate random but consistent context (person + background) for a pair."""
    ages = [25, 30, 35, 40, 45, 50, 55, 60]
    genders = ['man', 'woman']
    chosen_gender = random.choice(genders)
    
    # Feature combinations split by gender for logical consistency
    if chosen_gender == 'man':
        features_options = [
            "deep-set brown eyes and short dark hair",
            "hazel eyes and salt-and-pepper beard",
            "grey eyes and wavy brown hair",
            "amber eyes and short grey hair",
            "blue eyes and bald head with beard",
            "green eyes and messy blonde hair"
        ]
    else:  # woman
        features_options = [
            "bright blue eyes and shoulder-length blonde hair",
            "green eyes and curly red hair",
            "dark eyes and long black hair",
            "blue-green eyes and straight auburn hair",
            "hazel eyes and bob cut dark hair",
            "grey eyes and braided silver hair"
        ]
        
    # Background options (kept consistent for the pair)
    backgrounds = [
        "busy New York city street with blurred pedestrians",
        "quiet park bench under a large oak tree",
        "cozy living room with warm lighting",
        "modern office with glass windows",
        "misty mountain landscape",
        "seaside promenade with distant ocean",
        "library interior with bookshelves",
        "rustic cafe with wooden tables"
    ]
    
    # Lighting options (consistent for the pair)
    lightings = [
        "soft natural daylight",
        "cinematic golden hour lighting",
        "diffused window light",
        "dramatic studio lighting"
    ]

    return {
        'age': random.choice(ages),
        'gender': chosen_gender,
        'features': random.choice(features_options),
        'background': random.choice(backgrounds),
        'lighting': random.choice(lightings)
    }

def generate_detailed_prompt(expression, context):
    """
    Generate a detailed prompt using the shared context.
    """
    # Expression details
    if expression == 'sad':
        # Used for initial generation (fallback)
        emotion = "sad expression, looking down, melancholic, subtle tears"
    else:
        # Used for initial generation (primary)
        emotion = "happy expression, genuine smile, looking at camera, joyful"

    # Construct prompt with shared background/lighting
    prompt = f"""Generate a photorealistic image.
Medium shot portrait of a {context['age']}-year-old {context['gender']} with {context['features']}.
{emotion}.
Standing in a {context['background']}.
{context['lighting']}.
Hyper-realistic details: Visible skin pores, vellus hair, natural skin texture, sharp eyes.
Shot on Sony A7R V, 85mm G Master lens, f/1.8 aperture.
Raw photo, 8k resolution, highly detailed, photorealistic masterpiece.
No filters, natural look.
"""
    return prompt

def generate_image(client, model_name, prompt, output_path, input_image=None):
    """
    Generates an image.
    If input_image is provided, performs Image-to-Image editing (for consistency).
    Otherwise, performs Text-to-Image generation.
    """
    try:
        # Prepare contents
        if input_image:
            print(f"  > Editing image for consistency...")
            contents = [input_image, prompt]
        else:
            print(f"  > Generating new image...")
            contents = prompt

        # Call API
        response = client.models.generate_content(
            model=model_name,
            contents=contents
        )
        
        # Parse response for image blob
        image_data = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                    image_data = part.inline_data.data
                    break
        
        if image_data:
            image = Image.open(io.BytesIO(image_data))
            image.save(output_path)
            # Return PIL image for potential reuse (e.g., input to next step)
            return image
        else:
            print("  ✗ No image data found in response.")
            # print(f"  Response text: {response.text if response.text else 'None'}")
            return None

    except Exception as e:
        print(f"  ✗ Error generating image: {e}")
        return None

def main():
    # 1. Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return

    # 2. Configure Gemini API
    client = genai.Client(api_key=api_key)
    
    # Use Nano Banana (Gemini 2.5 Flash Image)
    model_name = 'models/gemini-2.5-flash-image'
    
    print(f"Initializing Image Generator using model: {model_name}")
    print("Using 1:1 CONSISTENCY MODE (Generate Happy -> Edit to Sad)...\n")

    # 3. Create output directory
    output_dir = "images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 4. Generate 10 pairs of images
    print("Starting generation of 10 pairs of images...")
    print("=" * 60)
    
    for i in range(1, 11):
        try:
            print(f"\n--- Generating Pair {i}/10 ---")
            
            # Generate context
            context = generate_pair_context()
            print(f"Subject: {context['age']}-year-old {context['gender']}")
            print(f"Stats: {context['features']}")
            print(f"Setting: {context['background']}")
            
            # 1. Generate HAPPY Image first (Base)
            prompt_happy = generate_detailed_prompt('happy', context)
            happy_path = os.path.join(output_dir, f"{i}_happy.png")
            
            print(f"Generating HAPPY base image...")
            happy_image = generate_image(client, model_name, prompt_happy, happy_path)
            
            if happy_image:
                print(f"  ✓ Saved: {i}_happy.png")
                
                # Delay
                time.sleep(2)

                # 2. Generate SAD Image by EDITING the Happy Image
                # This ensures 1:1 pixel consistency. Focus on NATURAL, authentic sadness across all facial muscles.
                prompt_sad_edit = "Make the person in this image look deeply and naturally sad. Keep the face structure, hair, lighting, pose, and background EXACTLY the same. Change the entire facial expression to reflect authentic melancholia: furrowed brows, heavy eyelids, downturned mouth, and a gaze full of sorrow. The sadness should look completely natural and human, not exaggerated."
                sad_path = os.path.join(output_dir, f"{i}_sad.png")
                
                print(f"Generating SAD variant (editing happy image)...")
                sad_image = generate_image(client, model_name, prompt_sad_edit, sad_path, input_image=happy_image)
                
                if sad_image:
                    print(f"  ✓ Saved: {i}_sad.png")
                else:
                    print(f"  ✗ Failed to generate sad variant.")
            else:
                print(f"  ✗ Failed to generate base happy image.")
            
        except Exception as e:
            print(f"✗ An unexpected error occurred for pair {i}: {e}")
            
        # Respect limit
        if i < 10:
            print("\nWaiting 2 seconds before next pair...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("Generation complete!")
    print(f"Check the '{output_dir}' directory for your images.")

if __name__ == "__main__":
    main()
