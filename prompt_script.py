import argparse
import json
from ollama import generate


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--consultation_file", type=str, help="Path to the consultation data.")
    args = parser.parse_args()

    return args

def create_prompt(consultation_data):
    """Generate a prompt for the LLM based on consultation data."""
    patient = consultation_data["patient"]
    consultation = consultation_data["consultation"]

    prompt = f"""
You are an assistant at a veterinary clinic. Please create discharge notes based on the following consultation details:

Patient Information:
- Name: {patient['name']}
- Species: {patient['species']}
- Breed: {patient['breed']}
- Gender: {patient['gender']}
- Neutered: {patient['neutered']}
- Date of Birth: {patient['date_of_birth']}
- Microchip: {patient['microchip']}
- Weight: {patient['weight']}

Consultation Details:
- Date: {consultation['date']}
- Time: {consultation['time']}
- Reason: {consultation['reason']}
- Type: {consultation['type']}
- Clinical Notes: { ' | '.join([f"{note['type'].capitalize()}: {note['note'].replace(chr(10), ' ')}" for note in consultation['clinical_notes']]) if consultation['clinical_notes'] else 'None' }
- Treatment Items:
  - Procedures: {' | '.join([f"{proc['name']} (Code: {proc['code']}, Date: {proc['date']}, Time: {proc['time']}, Quantity: {proc['quantity']}, Total Price: {proc['total_price']} {proc['currency']})" for proc in consultation['treatment_items'].get('procedures', [])]) if consultation['treatment_items'].get('procedures') else 'None'}
  - Medicines: {', '.join(consultation['treatment_items']['medicines']) if consultation['treatment_items'].get('medicines') else 'None'}
  - Prescriptions: {', '.join(consultation['treatment_items']['prescriptions']) if consultation['treatment_items'].get('prescriptions') else 'None'}
  - Foods: {', '.join(consultation['treatment_items']['foods']) if consultation['treatment_items'].get('foods') else 'None'}
  - Supplies: {', '.join(consultation['treatment_items']['supplies']) if consultation['treatment_items'].get('supplies') else 'None'}
- Diagnostics: {', '.join(consultation['diagnostics']) if consultation['diagnostics'] else 'None'}

Discharge Notes Formatting Instructions:
1. The output should include the following sections:
   - Discharge notes for "patient".
   - Summary of Consultation (a concise summary in  one paragraph with the available information). Please don't forget to include information about treatments such as procedures, medicines, prescripitions, foods, supplies and their prices.
   - Post-Consultation Care Instructions (in numbered list max 3). Please don't mention appointments and any type of medicine if there aren't any in the data. Only relevant advice. 
   - Next steps if there isn't any at the data say that we are available for any further questions or help.
2. Use only available information.
3. Ensure the notes are professional, clear, and easy to follow.

Create the discharge notes accordingly.
"""

    return prompt

def generate_discharge_notes(prompt):
    """Send the prompt to an LLM and get the discharge notes."""

    response = generate(model="mistral", prompt=prompt)

    return response['response']

def save_discharge_notes(consultation_file, discharge_notes):
    """Save discharge notes to a dynamically created file path."""
    
    discharge_notes = discharge_notes.replace("*", "")

    discharge_data = {"discharge_note": discharge_notes}

    base_name = os.path.splitext(os.path.basename(consultation_file))[0]
    
    new_file_name = f"{base_name}_solution.json"
    
    directory = os.path.dirname(consultation_file)
    new_file_path = os.path.join(directory, new_file_name)
    
    with open(new_file_path, "w") as file:
        json.dump(discharge_data, file, indent=4)
    
    print(f"Discharge notes saved to {new_file_path}")

if __name__ == "__main__":
    args = parse_arguments()


    with open(args.consultation_file) as consultation_data:
        data = json.load(consultation_data)

    prompt = create_prompt(data)

    #print(prompt)
    notes = generate_discharge_notes(prompt)

    #print(notes)

    save_discharge_notes(args.consultation_file, notes)
    
    