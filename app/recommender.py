
from embedding_utils import get_embedding, get_all_embeddings
from db_utils import fetch_product_by_name, fetch_all_products, fetch_product_category
from sklearn.metrics.pairwise import cosine_similarity
import re

# Product gender override for products where automatic detection fails
PRODUCT_GENDER_OVERRIDE = {
    "Men's Black T-Shirt": "Male",
    "Women's Floral Dress": "Female",
    "Unisex Hoodie": "Unisex",
    # Add more product mappings as needed
}

# Food product type classification
FOOD_TYPES = {
    'honey': ['honey', 'syrup', 'sweetener', 'spread'],
    'beverage': ['water', 'drink', 'soda', 'cola', 'juice', 'tea', 'coffee', 'coke'],
    'dairy': ['milk', 'yogurt', 'cheese', 'butter', 'cream'],
    'bakery': ['bread', 'cake', 'cookie', 'muffin', 'pastry'],
    'condiment': ['sauce', 'ketchup', 'mustard', 'dressing', 'vinegar', 'oil'],
    'snack': ['chip', 'cracker', 'popcorn', 'pretzel', 'nut'],
    'fruit': ['apple', 'banana', 'orange', 'grape', 'berry', 'fruit'],
    'vegetable': ['vegetable', 'carrot', 'potato', 'tomato', 'onion', 'broccoli'],
    'meat': ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'fish'],
}

def classify_food_type(product_name):
    """Determine food type based on product name"""
    product_name = product_name.lower()
    
    for food_type, keywords in FOOD_TYPES.items():
        for keyword in keywords:
            if keyword in product_name:
                return food_type
    
    return 'other'

def infer_gender_and_category_from_name(name, category=""):
    """Improved gender inference with more keywords"""
    name = name.lower()
    category = category.lower() if category else ""
    
    # Default gender and category
    gender = 'Unspecified'
    inferred_category = category if category else 'Unspecified'
    
    # Expanded gender keywords
    male_keywords = ['men', 'man', 'male', 'gent', 'gentleman', 'boy', 'his', 'him', 
                    'masculine', 'father', 'dad', 'boyfriend', 'brother']
    
    female_keywords = ['women', 'woman', 'female', 'lady', 'ladies', 'girl', 'her', 'she',
                      'feminine', 'mother', 'mom', 'girlfriend', 'sister']
    
    unisex_keywords = ['unisex', 'universal', 'all gender', 'any gender', 'neutral', 
                      'kids', 'children', 'baby', 'infant', 'toddler']
    
    # Check name for gender-specific keywords
    if any(word in name.split() or word in name for word in male_keywords):
        gender = 'Male'
    elif any(word in name.split() or word in name for word in female_keywords):
        gender = 'Female'
    elif any(word in name.split() or word in name for word in unisex_keywords):
        gender = 'Unisex'
    
    # Check category for gender hints
    if category:
        if any(word in category for word in male_keywords):
            gender = 'Male'
        elif any(word in category for word in female_keywords):
            gender = 'Female'
        elif any(word in category for word in unisex_keywords):
            gender = 'Unisex'
        
        # Handle specific categories with gender mapping (expanded)
        gender_category_map = {
            'beauty': ('Beauty', 'Female'),
            'cosmetic': ('Cosmetics', 'Female'),
            'makeup': ('Makeup', 'Female'),
            'fragrance': ('Fragrance', 'Female'),
            'perfume': ('Perfume', 'Female'),
            'cologne': ('Cologne', 'Male'),
            'shaving': ('Shaving', 'Male'),
            'furniture': ('Furniture', 'Unisex'),
            'groceries': ('Groceries', 'Unisex'),
            'food': ('Food', 'Unisex'),
            'beverage': ('Beverages', 'Unisex'),
            'home': ('Home', 'Unisex'),
            'decoration': ('Home Decorations', 'Unisex'),
            'protein': ('Supplements', 'Male'),
            'sport': ('Sports', 'Male'),
            'toy': ('Toys', 'Unisex'),
            'electronic': ('Electronics', 'Unisex'),
            'accessory': ('Accessories', 'Unisex')
        }
        
        for key, (mapped_category, mapped_gender) in gender_category_map.items():
            if key in category:
                inferred_category = mapped_category
                # Only override unspecified gender
                if gender == 'Unspecified':
                    gender = mapped_gender
    
    return gender, inferred_category

def get_recommendations(product_name, top_n=5):
    """
    Get product recommendations based on name, with gender information included
    """
    # Fetch target product
    target = fetch_product_by_name(product_name)
    if not target:
        return []
    
    # Get target product info
    target_name = target.get('name', '')
    target_description = target.get('description', '')
    target_category = fetch_product_category(target['id'])
    target_food_type = classify_food_type(target_name)
    
    # Check override first before inferring for target product
    if target_name in PRODUCT_GENDER_OVERRIDE:
        target_gender = PRODUCT_GENDER_OVERRIDE[target_name]
        # You might still want to infer category
        _, target_inferred_category = infer_gender_and_category_from_name(
            target_name, target_category
        )
    else:
        # Infer gender for target product
        target_gender, target_inferred_category = infer_gender_and_category_from_name(
            target_name, target_category
        )
    
    # Get embeddings
    target_embedding = get_embedding(f"{target_name}. {target_description}")
    all_products = fetch_all_products()
    all_embeddings = get_all_embeddings()
    
    # Create scoring function
    results = []
    for i, product in enumerate(all_products):
        if product['id'] == target['id']:  # Skip the target product
            continue
        
        product_name = product.get('name', '')
        product_food_type = classify_food_type(product_name)
        product_category = fetch_product_category(product['id'])
        
        # Check override first before inferring for comparison product
        if product_name in PRODUCT_GENDER_OVERRIDE:
            product_gender = PRODUCT_GENDER_OVERRIDE[product_name]
            # You might still want to infer category
            _, product_inferred_category = infer_gender_and_category_from_name(
                product_name, product_category
            )
        else:
            # Infer gender for comparison product
            product_gender, product_inferred_category = infer_gender_and_category_from_name(
                product_name, product_category
            )
        
        # Base similarity score from embeddings
        content_score = cosine_similarity([target_embedding], [all_embeddings[i]])[0][0]
        
        # Strong penalty for mixing beverages with non-beverages
        food_type_compatibility = 1.0
        if target_food_type == 'beverage' and product_food_type != 'beverage':
            food_type_compatibility = 0.2
        elif target_food_type != 'beverage' and product_food_type == 'beverage':
            food_type_compatibility = 0.2
            
        # Strong bonus for same food type
        food_type_score = 1.0 if target_food_type == product_food_type else 0.3
        
        # Category match
        category_score = 0.8 if target_category == product_category else 0.2
        
        # Gender compatibility score
        gender_score = 1.0  # Default is compatible
        
        # Apply gender compatibility logic
        if target_gender != 'Unspecified' and product_gender != 'Unspecified':
            if target_gender != product_gender and target_gender != 'Unisex' and product_gender != 'Unisex':
                # Penalize if genders are specified but incompatible
                gender_score = 0.2
        
        # Calculate final score with weights for all factors
        final_score = (
            0.25 * content_score + 
            0.25 * category_score + 
            0.25 * food_type_score +
            0.25 * gender_score
        ) * food_type_compatibility  # Apply compatibility penalty if needed
        
        # Add complete product data with additional metadata
        enhanced_product = {
            **product,  # Original product data
            'gender': product_gender,
            'inferred_category': product_inferred_category,
            'food_type': product_food_type,
            'score': final_score
        }
        
        results.append((enhanced_product, final_score))
    
    # Sort by final score
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N products with full details
    return [product for product, _ in results[:top_n]]

def explain_recommendations(target_product, recommendations):
    """Provide detailed explanations for why each product was recommended"""
    explanations = []
    target_name = target_product.get('name', '')
    target_food_type = classify_food_type(target_name)
    
    # Check override first before inferring for target product
    if target_name in PRODUCT_GENDER_OVERRIDE:
        target_gender = PRODUCT_GENDER_OVERRIDE[target_name]
        target_category = target_product.get('category', '')
    else:
        target_gender, target_category = infer_gender_and_category_from_name(
            target_name, target_product.get('category', '')
        )
    
    for product in recommendations:
        product_name = product.get('name', '')
        product_food_type = product.get('food_type', classify_food_type(product_name))
        product_gender = product.get('gender', 'Unspecified')
        product_category = product.get('inferred_category', product.get('category', ''))
        
        explanation = f"{product_name}: "
        
        reasons = []
        
        # Add food type explanation
        if target_food_type == product_food_type:
            reasons.append(f"similar type of food ({product_food_type})")
        
        # Add gender compatibility explanation
        if target_gender != 'Unspecified' and product_gender != 'Unspecified':
            if target_gender == product_gender:
                reasons.append(f"designed for the same gender ({product_gender})")
            elif target_gender == 'Unisex' or product_gender == 'Unisex':
                reasons.append(f"compatible gender targeting (one is unisex)")
        
        # Find related terms
        target_terms = set(re.findall(r'\b\w+\b', target_name.lower()))
        product_terms = set(re.findall(r'\b\w+\b', product_name.lower()))
        common_terms = target_terms.intersection(product_terms)
        common_terms = [t for t in common_terms if len(t) > 2 and t not in {'the', 'and', 'for'}]
        
        if common_terms:
            reasons.append(f"shares terms: {', '.join(common_terms)}")
        
        # Add category explanation
        if target_category == product_category and target_category != 'Unspecified':
            reasons.append(f"same product category ({product_category})")
        
        # If no specific reasons found
        if not reasons:
            reasons.append("complementary item based on overall similarity")
        
        explanation += "; ".join(reasons)
        explanations.append(explanation)
    
    return explanations

