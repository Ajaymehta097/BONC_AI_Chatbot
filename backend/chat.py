import json
import faiss
import numpy as np
import re
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# 1. INITIALIZATION: Load AI Model & BONC Database
# --------------------------------------------------
print("Loading BONC AI Model & Database... Please wait.")
model = SentenceTransformer('all-MiniLM-L6-v2')

index = faiss.read_index("b2b_index.faiss")
with open("metadata.json", "r", encoding="utf-8-sig") as f:
    metadata = json.load(f)

# --------------------------------------------------
# 2. HELPER FUNCTION: Detect Language
# --------------------------------------------------
def detect_language(query):
    """Detect if the user is asking in Hindi/Hinglish or English"""
    hinglish_words = ['mujhe', 'batao', 'kya', 'hai', 'kaise', 'kon', 'chahiye', 'dikhao', 'kaha', 'wala', 'do', 'kidhar']
    query_words = query.lower().split()
    
    if any(word in query_words for word in hinglish_words):
        return "hinglish"
    return "english"

# --------------------------------------------------
# 3. LAYER 1: Rule-Based Engine (Fast Responses)
# --------------------------------------------------
def rule_based_engine(user_query):
    """Handles basic greetings and strict BONC platform queries"""
    query = user_query.lower()
    
    # Greetings
    if re.search(r'\b(hi|hello|hey|namaste)\b', query):
        return "Hello! I am the official BONC Network AI Assistant. I can help you find verified B2B products, categories, and companies. What are you looking for today?"
    
    # Support/Contact
    if re.search(r'\b(contact|phone|email|support|help|madad)\b', query):
        return "You can reach the BONC support team at support@boncnetwork.com or call our toll-free number."
    
    return None # If no rule matches, send to AI (Layer 2)

# --------------------------------------------------
# 4. LAYER 2: Strict AI Vector Search Engine with Location Extractor
# --------------------------------------------------
def vector_search_engine(user_query):
    """Searches the BONC database strictly and accurately"""
    lang_mode = detect_language(user_query)
    
    # Set dialogues based on language
    if lang_mode == "hinglish":
        intro_text = "✅ BONC Network par aapke liye yeh best matches mile hain:\n"
        not_found_text = "🚫 Maaf kijiye, par BONC Network ke catalog mein mujhe iski koi jankari nahi mili. Kripya kisi B2B product, dealer, ya company ke baare mein puchein."
        business_label = "🏢 Business/Product"
        desc_label = "📝 Details"
    else:
        intro_text = "✅ Here are the most accurate matches from the BONC Network:\n"
        not_found_text = "🚫 I'm sorry, I couldn't find that in the BONC Network catalog. I can only assist you with B2B products, verified dealers, and categories available on our platform."
        business_label = "🏢 Business/Product"
        desc_label = "📝 Details"

    # 🌟 NEW: Query Cleaner (Hinglish words ko search se pehle remove karna)
    hinglish_noise = ['mujhe', 'batao', 'kya', 'hai', 'kaise', 'kon', 'chahiye', 'dikhao', 'kaha', 'wala', 'do', 'kidhar', 'ke', 'area', 'me', 'milenge']
    clean_query = user_query.lower()
    for word in hinglish_noise:
        # Faltu words ko hatana
        clean_query = re.sub(rf'\b{word}\b', '', clean_query)
    clean_query = clean_query.strip()
    
    # Agar clean karne ke baad query empty ho jaye, toh original query use karo
    if not clean_query:
        clean_query = user_query

    # Convert CLEAN query to Vector
    query_vector = model.encode([clean_query]).astype('float32')
    distances, indices = index.search(query_vector, k=2)
    
    # 🔴 RELAXED ACCURACY LIMIT: 1.20 (Allows AI to match despite minor spelling/context differences)
    THRESHOLD = 1.20 
    
    response = intro_text
    found_match = False
    
    for i, idx in enumerate(indices[0]):
        if idx != -1 and distances[0][i] < THRESHOLD: 
            found_match = True
            matched_meta = metadata[idx]
            source_data = matched_meta['source_data']
            
            # 1. Find the best name
            name = (source_data.get('Name') or 
                    source_data.get('SubCategoryName') or 
                    source_data.get('CompanyName') or 
                    source_data.get('BusinessName') or 
                    source_data.get('Title'))
            
            if not name and 'MetaTitle' in source_data:
                name = source_data['MetaTitle'].split('|')[0].strip()
            if not name:
                name = "Verified BONC Supplier"
                
            response += f"\n{business_label}: {name}\n"
            
            # 2. Clean and add Description
            description = source_data.get('Description') or source_data.get('MetaDescription')
            if description:
                desc_clean = description.replace('on Bonc Network', '').replace('  ', ' ').strip()
                response += f"   {desc_label}: {desc_clean}\n"
            
            # 3. Extract Location Data 📍
            location_info = []
            location_keywords = ['city', 'state', 'address', 'location', 'pincode', 'district', 'country']
            
            for key, value in source_data.items():
                if value and any(loc in key.lower() for loc in location_keywords):
                    location_info.append(str(value))
            
            if location_info:
                # Remove duplicates but keep order
                unique_locations = list(dict.fromkeys(location_info))
                response += f"   📍 Location: {', '.join(unique_locations)}\n"

            # 4. Filter out SEO, System IDs, and Location keys (so they don't print twice)
            ignore_keywords = ['id', 'created', 'updated', 'path', 'slug', 'isactive', 'by', 
                               'meta', 'robots', 'canonical', 'author', 'publisher', 'language', 'url', 'enabled', 'name', 'title', 'description'] + location_keywords
            
            # 5. Format remaining useful details
            for key, value in source_data.items():
                if value and not any(ignored in key.lower() for ignored in ignore_keywords):
                    readable_key = ''.join([' '+c if c.isupper() else c for c in key]).strip().capitalize()
                    response += f"   - {readable_key}: {value}\n"
    
    if found_match:
        return response
    else:
        return not_found_text

# --------------------------------------------------
# 5. HYBRID CONTROLLER
# --------------------------------------------------
def get_chatbot_response(user_query):
    """Routes the query to Rules first, then AI if needed"""
    rule_response = rule_based_engine(user_query)
    if rule_response:
        return rule_response
    return vector_search_engine(user_query)

# --------------------------------------------------
# 6. TERMINAL RUNNER (For Testing in VS Code)
# --------------------------------------------------
if __name__ == "__main__":
    print("\n✅ BONC AI Chatbot is Ready! Type 'exit' to stop.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Closing BONC AI...")
            break
        
        answer = get_chatbot_response(user_input)
        print(f"BONC AI:\n{answer}")