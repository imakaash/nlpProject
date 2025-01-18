
# Automobile Coding Task

This file walks you through the implementation of an application that can take unstructured prompts written by the user and convert them into a structured request body using `spaCy` which may look something like below.

{
    'modelTypeCodes': ['21EM'], 
    'booleanFormulas': ['-S402A+P7LGA'], 
    'dates': ['2024-11-08']
}

## Dependencies

The following notebook uses the below mentioned libraries for information extraction (can also be found in the 'requirements.txt' file). The same can be installed through the notebook by running the first cell.

```
dateparser==1.1.8
spacy==3.5.2
fuzzywuzzy==0.18.0
```

## Installation

```
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

## Files

- **BMWGroupCodingTaskAkash.ipynb**: Contains the Handler class, which processes natural language user prompts and extracts information required to create a request body. It also has testing and some observations present.
- **BMWGroupCodingTaskAkash.py**: This files contains the same code and can be used to call from the terminal. (Section: Running from Terminal)
- **user_prompts.xlsx**: Contains the prompts and expected output to be generated from them. Only used for testing.
- **requirements.txt**: Contains a list of libraries on which the application is dependent and required to be installed (Section: Installation)

## Usage

To use the Handler class, simply create an instance of it and pass in the user prompt as a string. Then call the *'get_request_body()'* method on the instance to obtain the request body.

## Testing

The notebook has 5 sections:
- *Main code*: This module creates the Handler class, which processes text and extracts information related to model codes, dates, and boolean formulas.
- *Testing with the given user prompt*: This section defines a list of test user prompts and then loops through each prompt in the list. Within the loop, it creates an instance of the Handler class, passing the string as an argument to the constructor. It then calls the 'get_request_body()' method of the Handler instance to obtain the request body associated with the given user prompt. (**Note**: This section can be used to test multiple prompts by adding them to the list. Please run the cells under 'Main code' before to compile the class.)
- *Test cases*: This module has test cases which uses the assertEqual method to compare the expected output with the actual output of the application along with the same level of testing using pandas dataframe with prompts loaded in a excel file for display of results.
- *Valid prompts*: Includes demo for the validation to ensure the prompts entered by the user are valid and allowing the user to modify the prompt before sending the request. (**Note**: This section can be used to test random prompts one by one. Please run the cells under 'Main code' before to compile the class.)
- *Some more use cases*: Has some boundary test cases with comments and observations.

## Running from Terminal

To execute the script from terminal, the below command can be used by opening the terminal at the respective directory. Once ran, it asks for the prompt to be feeded into the Application recursively.

```
python BMWGroupCodingTaskAkash.py
```
