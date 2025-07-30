from google import genai

project = ""

with open("project.txt") as f:
  project = f.readline()



client = genai.Client(
      vertexai=True,
      project=project,
      location="global",
  )

si_text1 = """ You are a highly imaginative AI assistant. Fulfill user requests with ingenuity and resourcefulness, providing innovative and effective solutions while adhering to instructions. """

model = "gemini-2.5-flash"


generate_content_config = genai.types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.9,
    max_output_tokens = 2048,
    response_mime_type = "text/x.enum",
    system_instruction=[genai.types.Part.from_text(text=si_text1)],
    thinking_config=genai.types.ThinkingConfig(
      thinking_budget=10,
    ),
  )



def generate_idea(query: str, concise:bool=True) -> str:

  if concise:
    text = f"Provide one idea on a given topic: {query}, make responce short"
  else:
    text = f"Write one comprehencive, but short description that contains all necessary information about the title: {query}"

  contents = [
    genai.types.Content(
      role="user",
      parts=[
        genai.types.Part.from_text(text=text)
      ]
    ),
  ]
  
  responce = ""
  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):

    
    responce += chunk.text

  return responce
