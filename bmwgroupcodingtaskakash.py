# -*- coding: utf-8 -*-

# BMW Group Coding Task

"""##1. Main code"""

# Importing the libraries
import spacy
from spacy import displacy
import datetime
import dateparser
from dateparser.search import search_dates
from fuzzywuzzy import fuzz
import re
import logging
import pandas as pd
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

class Handler:
    """
    This is a brief description of what the Handler class does.
    This module defines the Handler class, which processes text and extracts information related to model codes, dates, and boolean formulas.
    
    Attributes:
    -----------
    text : str
      The text to be processed by the Handler class.
    response : int
      A binary flag indicating if the text was successfully processed (1) or not (0).
    message : str
      A message indicating the success or failure of the text processing.
    dates : str
        A datetime object representing the dates mentioned in the text in the 'YYYY-MM-DD' format.
    model_code : list
      A list of model codes for Sales Description mentioned in the text.
    boolean_formula : str
      A string representing abbreviation mentioned in the Sales Description extracted from the text.
    
    Methods:
    --------
    init(text):
      Initializes the Handler class with the given text.
    get_doc():
      For retreiving SpaCy document.
    validator():
      For validation of the given user promts feeded to the Application.
    get_model_codes(doc):
      Extracts the model codes from the SpaCy document.
    get_parsed_dates(doc):
      Extracts the dates mentioned in the text and converts them to string from datetime objects.
    get_boolean_formula(doc):
      Extracts the boolean formula from the text based on a logic.
    get_request_body():
      Generates the request body based on the extracted information.
    """

    # Identifier
    def __init__(self, text):
      """
      Initializes the Handler class with the given text.

      Parameters:
      -----------
      text : str
          The text to be processed by the Handler class.
      """

      self.text = text.lower()
      self.response = 0
      self.message = ""

      self.dates = ""
      self.model_code = []
      self.boolean_formula = ""

      # Creating a dictionary for storing the model codes
      # The exhaustive list can be retrieved from the database but for now can be considered to be hardcoded.
      self.model_codes_dic = {
        '21CF': 'iX xDrive50',
        '11CF': 'iX xDrive40',
        '21EM': 'X7 xDrive40i',
        '21EN': 'X7 xDrive40d',
        'DZ01': 'M8',
        '28FF': '318i'
      }

      self.abbreviations_dic = {
        'LL': 'Left-Hand Drive',
        'RL': 'Right-Hand Drive',
        'P337A': 'M Sport Package',
        'P33BA': 'M Sport Package Pro',
        'P7LGA': 'Comfort Package EU',
        'S402A': 'Panorama Glass Roof',
        'S407A': 'Panorama Glass Roof Sky Lounge',
        'S403A': 'Sunroof'
      }

      # Calling methods internally
      self.validator(self.get_doc())

    # For retreiving SpaCy document
    def get_doc(self):
      """
      This method lets you retrieve the spacy document.

      Parameters:
      -----------
      None

      Returns:
      --------
      doc : spacy.tokens.doc.Doc
          The Spacy document object to be processed.
      """
      # Loading the Spacy English language model
      nlp = spacy.load('en_core_web_md')
      doc = nlp(self.text)

      return doc

    # For validating of user prompts
    def validator(self, doc):
      """
      This method lets you validate the user prompts.

      Parameters:
      -----------
      doc : spacy.tokens.doc.Doc
        The Spacy document object to be processed.

      Returns:
      --------
      None
      """

      try:
        # Validating the individual tokens
        for token in doc:
          if token.is_oov: # This fails if you are using 'en_core_web_sm', i.e, a smaller vocabulary
            if token.text not in ''.join(self.model_codes_dic.values()).lower():
              self.response = 0
              message = "Prompt has some Out-of Vocabulary words: {}, Please check!".format(token.text)
              self.message += ". " + message
            break
          self.response = 1

        # Validating the model codes
        if self.response == 1:
          self.get_model_codes(self.get_doc())
          if len(self.model_code) == 0:
            self.response = 0
            message = "Prompt doesn't include one of the sales description provided, Please check!"
            self.message += ". " + message

        # Validating on sales description/ abbreviations
        if self.response == 1:
          self.get_boolean_formula(self.get_doc())
          if len(self.boolean_formula) == 0:
            self.response = 0
            message = "Prompt doesn't include a valid abbreviation description, Please check!"
            self.message += ". " + message
        
        # Validation on dates
        if self.response == 1:
          self.get_parsed_dates(self.get_doc())
          if len(self.dates) == 0:
            self.response = 0
            message = "Prompt doesn't include a valid date, Please check!"
            self.message += ". " + message

        if self.response == 1:
          self.get_request_body()

      except Exception as e:
        # If any exception occurs, set the response flag to 0 and log the error message
        self.response = 0
        message = "Error while validating the prompts"
        self.message += ". " + message
        self.message += ". " + str(e)

    # Method 1
    def get_model_codes(self, doc):
      """
      This method generates model codes based on a pre-defined dictionary of Sales description
      in the input text from the Spacy document.

      Parameters:
      -----------
      doc : spacy.tokens.doc.Doc
          The Spacy document object to be processed.

      Returns:
      --------
      None
      """

      try:
        # Extracting text from the SpaCy document
        text = doc.text

        # Single Request Prompts
        # Check if any of the model code values are present in the features
        model_code = []

        for value in self.model_codes_dic.values():
          if value.lower() in text:
            for i in self.model_codes_dic:
              if self.model_codes_dic[i] == value:
                model_code.append(i)
                text = text.replace(value.lower(), "")

        # Multiple Request Prompts
        # We use partial match to get multiple prompts
        if len(text) > 0:
          for value in self.model_codes_dic.values():
            lst = value.lower().split()
            for v in lst:
              # Calculate the fuzzy similarity between the token and each word in the sentence
              similarity_scores = [fuzz.ratio(v, word) for word in text.replace(',','').split()]
              if max(similarity_scores) == 100:
                # If the fuzzy match score is 100, add the corresponding key to the list of model codes
                for i in self.model_codes_dic:
                  if self.model_codes_dic[i]==value:
                    model_code.append(i)
              break

        self.response = 1

        if self.response == 1:
          self.model_code = model_code

      except Exception as e:
        # If any exception occurs, set the response flag to 0 and log the error message
        self.response = 0
        message = "Error encountered while parsing for model code in 'get_model_codes' method"
        self.message += ". " + message
        self.message += ". " + str(e)

    # Method 2
    def get_boolean_formula(self, doc):
      """
      This method generates a boolean formula based on a pre-defined dictionary of abbreviations
      and conjunction words in the input text from the Spacy document.

      Parameters:
      -----------
      doc : spacy.tokens.doc.Doc
          The Spacy document object to be processed.

      Returns:
      --------
      None
      """

      try:
        # Creating the token, direction and features (such as POS etc.) dataframe using parse_deps of displacy for 
        # relationship extraction
        features = []
        words_df = pd.DataFrame(displacy.parse_deps(doc)['words'])
        arcs_df = pd.DataFrame(displacy.parse_deps(doc)['arcs'])
        for token in doc:
          features.append({'TEXT' : token.text, 'LEMMA' : token.lemma_, 'POS' : token.pos_, 'TAG' : token.tag_, 'DEP' : token.dep_,
                    'SHAPE' : token.shape_, 'ALPHA' : token.is_alpha, 'STOP': token.is_stop, 'OOV': token.is_oov})

        fdf = pd.DataFrame(features)

        # Abbreviation string
        desc_str = ' '.join(list(fdf[fdf['POS'].isin(['PROPN', 'NOUN', 'VERB', 'ADJ', 'CCONJ', 'PUNCT'])]['TEXT']))

        # For storing boolean formula and conjugation and adposition words
        boolean_formula = ""
        conj_df = fdf[fdf['DEP'].isin(['cc', 'punct']) & fdf['TEXT'].isin(['and', 'or', ',', '.'])]
        adp_df = words_df[words_df['tag'] == 'ADP']

        # This block of code checks if there are conjunctions in the text and then creates a substring for further 
        # processing
        if len(list(conj_df['TEXT'])) == 0:
          split_sentence = [desc_str]
        else:
          # Escape special characters for regex
          split_words = [(r"\b" + re.escape(word) + r"\b") for word in list(conj_df['TEXT'])]
          split_words.append(',')
          split_words.append(re.escape('.'))
          split_regex = "|".join(split_words)
          # Spliting sentence using regex
          split_sentence = re.split(split_regex, desc_str)

        # Storing the matched specifications into the list
        abreviation_match_lst = []
        for desc_str_brk in split_sentence:
          desc_str_brk = ''.join(desc_str_brk.split())
          key_at_index = ''
          while True:
            # Calculating the fuzzy similarity between the description and the token extracted from prompts
            similarity_scores = []
            for value in self.abbreviations_dic.values():
              similarity_score = fuzz.partial_ratio(value.lower().replace(' ',''), desc_str_brk)
              similarity_scores.append(similarity_score)
            
            # Setting breaking criteria
            if max(similarity_scores) < 85:
              break

            # Get the index of the highest similarity score
            max_index = len(similarity_scores) - similarity_scores[::-1].index(max(similarity_scores)) - 1
            key_list = list(self.abbreviations_dic.keys())
            key_at_index = key_list[max_index]

            # Removing the found match word for next iteration
            remove_words = self.abbreviations_dic[key_at_index].lower().split()
            for word in remove_words:
              desc_str_brk = desc_str_brk.replace(word, "", 1)

          # Appending to the match list
          abreviation_match_lst.append(key_at_index)

        # Synonyms for 'with'/'without'
        synonym_w = ['with', 'accompanied', 'company', 'together', 'addition', 'including', 'along', 'amidst', 'among', 'amid', 'having', 'in']
        synonym_wo = ['without', 'lacking', 'deprived', 'not', 'missing', 'destitute', 'bereft', 'deficient', 'void', 'unaccompanied', 'except', 'exclusive']

        # To check if brackets are required
        first, second = False, False  
        if len(set(list(conj_df['TEXT'])).intersection(set(['and', 'or']))) > 1:
          # For placing brackets
          brkt_df = arcs_df[arcs_df['label'] == 'cc']
          brkt_df['diff'] = brkt_df['end'] - brkt_df['start']
          brkt_df['needed'] = brkt_df['diff'].apply(lambda x: 1 if x>1 else 0)

          # To check which group of specifications to bind
          if list(brkt_df['needed'])[0] > list(brkt_df['needed'])[1]:
            second = True
          else:
            first = True

        # This block of code checks if there are conjunctions in the text and then creates a boolean formula accordingly
        if len(list(conj_df['TEXT'])) == 0:
          split_sentence = [self.text]
        else:
          # Escape special characters for regex
          split_words = [(r"\b" + re.escape(word) + r"\b") for word in list(conj_df['TEXT'])]
          split_words.append(',')
          split_words.append(re.escape('.'))
          split_regex = "|".join(split_words)
          # Spliting sentence using regex
          split_sentence = re.split(split_regex, self.text)

        opertor = ""
        bracket = ""
        for ind, text in enumerate(split_sentence):
          # Check if the text fragment contains 'and' or 'or' as conjunction
          conj = ""
          if ind > 0:
            conj = "/" if list(conj_df['TEXT'])[ind-1] == 'or' else ""

          # Check if the text fragment contains a synonym for 'with' or 'without'
          if len(set(synonym_wo).intersection(set(text.split()))) > 0:
            opertor = "-"
          elif len(set(synonym_w).intersection(set(text.split()))) > 0:
            opertor = "+"
          else:
            opertor = opertor
          
          if len(abreviation_match_lst[ind])>0:
            # Inserting the brackets, conjunctions and operator, if required
            if first == True:
              tot = sum([1 if itm in boolean_formula and itm != '' else 0 for itm in abreviation_match_lst])
              if tot == 0:
                bracket = "("
              else:
                bracket = ""
            
            if second == True:
              tot = sum([1 if itm in boolean_formula and itm != '' else 0 for itm in abreviation_match_lst])
              if tot == 1 and len(boolean_formula)>0:
                bracket = "("
              else:
                bracket = ""

            boolean_formula += conj+opertor+bracket
            bracket = ""

            # Inserting the brackets, if required
            if first == True:
              tot = sum([1 if itm in boolean_formula and itm != '' else 0 for itm in abreviation_match_lst])
              if tot == 1 and len(boolean_formula)>0:
                bracket = ")"
              else:
                bracket = ""

            if second == True:
              tot = sum([1 if itm in boolean_formula and itm != '' else 0 for itm in abreviation_match_lst])
              if tot == 2 and len(boolean_formula)>0:
                bracket = ")"
              else:
                bracket = ""

          boolean_formula += abreviation_match_lst[ind]+bracket
          bracket = ""

        # Check for all elements appended to the string
        if sum([0 if word in boolean_formula else 1 for word in abreviation_match_lst])>0:
          for word in abreviation_match_lst:
            if not word in boolean_formula:
              boolean_formula += boolean_formula[0] + word
              
        # Set response flag to 1 and store the boolean formula in the object
        self.response = 1

        if self.response == 1:
          self.boolean_formula = boolean_formula

      except Exception as e:
        # If any exception occurs, set the response flag to 0 and log the error message
        self.response = 0
        self.boolean_formula = ""
        message = "Error encountered while parsing for a valid abbreviation description in 'get_boolean_formula' method"
        self.message += ". " + message
        self.message += ". " + str(e)
    
    # Method 3
    def get_parsed_dates(self, doc):
      """
      This method extracts dates from the input text of Spacy document and returns a date in the format 'yyyy-mm-dd'.

      Parameters:
      -----------
      doc : spacy.tokens.doc.Doc
          The Spacy document object to be processed.

      Returns:
      --------
      None
      """

      try:
        # Extract all entities that have the label 'DATE' and get the last one
        dt = [entity.text for entity in doc.ents if entity.label_ == "DATE" or entity.label_ == "CARDINAL"]

        # Check if the last date contains any of the keywords that indicate the start of a period
        if len(set(['late', 'latter', 'end']).intersection(set(self.text.split()))) > 0:
          # If no, prefer the last day of the month for the date extraction
          dates = search_dates(dt[-1], settings={'PREFER_DAY_OF_MONTH': 'last'})
        else:
          dates = search_dates(dt[-1], settings={'PREFER_DAY_OF_MONTH': 'first'})
        
        # Format the datetime object to "yyyy-mm-dd" format
        dt = dates[-1][1].strftime('%Y-%m-%d')
      
        # Set response flag to 1 and store the date
        self.response = 1

        if self.response == 1:
          self.dates = dt

      except Exception as e:
        # If any exception occurs, set the response flag to 0 and log the error message
        self.response = 0
        message = "Error encountered while parsing for date in 'get_parse_dates' method"
        self.message += ". " + message
        self.message += ". " + str(e)
    
    def get_request_body(self):
      """
      This method generates the request body based on the extracted information.

      Parameters:
      -----------
      None

      Returns:
      --------
          : dict or list
          The request body generated is returned.
      """

      try:
        if self.response == 1: # If there was no error while parsing information
          if len(self.model_code) == 1: # If only one model code is provided
            return {'modelTypeCodes': [self.model_code[0]],
                    'booleanFormulas': [self.boolean_formula],
                    'dates': [self.dates]}
          else: # If multiple model codes are provided
            lst = []
            for model_code in self.model_code:
              lst.append({'modelTypeCodes': [model_code],
                    'booleanFormulas': [self.boolean_formula],
                    'dates': [self.dates]})
            return lst

        else: # If there was an error while parsing information
          return {'message': [self.message.strip(". ")]}

      except Exception as e: # If there was any other error
        self.response = 0
        message = "Error encountered while creating of request body in 'get_request_body' method"
        self.message += ". " + message
        self.message += ". " + str(e)
        return self.get_request_body()


if __name__ == '__main__':
  while True:
    string = input("Enter the prompt: ")
    print("User prompt: " + string)
    
    # Creating object of the Handler class and calling the method to get the request body
    obj = Handler(string)
    print("Request Body: \n", obj.get_request_body())

    print("\n")

    # check the condition
    if len(obj.message) == 0 or obj.response == 1:
        break

    print("Try again!!\n")
