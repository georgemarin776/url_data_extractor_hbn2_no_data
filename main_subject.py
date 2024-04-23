from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load a BERT model designed for feature extraction
feature_extractor = pipeline('feature-extraction', model='bert-base-uncased', tokenizer='bert-base-uncased', device=0)

# Input terms
terms = ["diamond", "blue", "short", "dress"]

# Validate that terms are provided
if not terms:
    raise ValueError("No terms provided. The terms list is empty.")

# Extract features with BERT (using CLS token)
features = np.squeeze(feature_extractor(terms))

# Validate feature extraction
if features.ndim == 1:
    # This implies there was only one term and features are directly the vector
    features = np.expand_dims(features, axis=0)
elif features.size == 0:
    raise ValueError("Feature extraction failed. No features extracted.")

# Calculate norms of features to determine the main subject
norms = np.linalg.norm(features, axis=1)
if norms.size == 0:
    raise ValueError("Norm calculation failed. No norms computed.")

# Validate norms and determine main subject index
if not isinstance(norms, np.ndarray) or norms.size != len(terms):
    raise ValueError("Norm array mismatch with terms array.")
main_subject_index = np.argmax(norms)

# Validate index and access main subject
if main_subject_index >= len(terms):
    raise IndexError("Calculated index is out of range for terms list.")
main_subject = terms[main_subject_index]

# Load Sentence Transformer model for similarity comparison
model = SentenceTransformer('all-MiniLM-L6-v2')
main_subject_embedding = model.encode(main_subject, convert_to_tensor=True)
attribute_embeddings = model.encode([term for term in terms if term != main_subject], convert_to_tensor=True)

# Calculate similarities
similarity_scores = util.cos_sim(main_subject_embedding, attribute_embeddings)

print(f"Main Subject: {main_subject}")
for term, score in zip([term for term in terms if term != main_subject], similarity_scores[0]):
    print(f"Similarity between '{main_subject}' and '{term}': {score.item()}")
