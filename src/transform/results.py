import pandas as pd

def transform_results_df(
    df_in,
    *,
    raw_id,
    keyword,
    page,
    pulled_at,
    module_type,
    module_label,
    module_index):
    """
    Take a raw shopping-results DataFrame for a single module
    and return a cleaned, standardized results DataFrame.

    - Drops unused SerpAPI fields
    - Normalizes `multiple_sources` to boolean
    - Renames extracted price fields
    - Adds module + search context columns
    - Reorders columns to match `stg_results` schema
    """
    # Work on a copy to avoid mutating the original input
    transform_df = df_in.copy()

    # 1) Drop columns we decided not to stage
    transform_df = transform_df.drop(columns=['snippet', 'price', 'delivery', 'old_price', 'thumbnail',
                                             'extensions', 'source_icon', 'product_link', 'serpapi_thumbnail', 
                                            'immersive_product_page_token', 'serpapi_immersive_product_api'],
                                    errors='ignore')

    # 2) Convert multiple_sources -> proper bool
    if 'multiple_sources' in transform_df:
        transform_df['multiple_sources'] = (
            transform_df['multiple_sources'].replace('True', True).fillna(False).astype(bool))
    else:
        transform_df['multiple_sources'] = False

    # 3) Create and nullify block_position for results which lack this field
    transform_df["block_position"] = transform_df.get("block_position", None)

    # 4) Rename fields to final names
    transform_df = transform_df.rename(columns={
        'position': 'position_in_module',
        'extracted_price': 'price',
        'extracted_old_price': 'old_price'
    })

    # 5) Attach module + search context
    transform_df = transform_df.assign(
        module_type=module_type,
        module_label=module_label,
        module_index=module_index,
        raw_id=raw_id,
        keyword=keyword,
        page=page,
        pulled_at=pulled_at
    )

    # 6) Reorder columns to match target table
    final_cols = [
    "raw_id",
    "keyword",
    "page",
    "pulled_at",
    "title",
    "product_id",
    "price",
    "old_price",
    "reviews",
    "rating",
    "source",
    "multiple_sources",
    "tag",
    "module_type",
    "module_label",
    "module_index",
    "block_position",
    "position_in_module"
    ]
    transform_df = transform_df.reindex(columns=final_cols)
    
    return transform_df


def build_results_for_keyword(keyword_raw):
    """
    Build a full results DataFrame for ONE raw keyword request row.

    Steps:
    - Pull raw_id / keyword / page / pulled_at from df_raw
    - Flatten `shopping_results` (all products)
    - Flatten each entry in `categorized_shopping_results`
    - Run everything through `transform_results_df`
    - Union uncategorized + categorized into one DataFrame
    """
     # 1) Grab the first raw row (later this will be parameterized / looped)
    keyword_search = keyword_raw

     # 2) Extract search metadata used for context columns
    raw_id, pulled_at, keyword, page = keyword_search.loc[['id', 'pulled_at', 'keyword', 'page']]

    # 3) Extract JSON extract from the keyword request
    keyword_json = keyword_search.loc['response_json']

    # 4) Create a blank dataframe list
    df_list = []

    # 5) Build uncategorized results
    uncategorized_df_raw = pd.DataFrame(keyword_json.get('shopping_results', []))
    uncategorized_df_clean = transform_results_df(uncategorized_df_raw, 
                                                raw_id=raw_id, pulled_at=pulled_at, keyword=keyword, page=page,
                                                module_type='all_products', module_label='All products', module_index=99)
    
    df_list.append(uncategorized_df_clean)

    # 6) (If they exist) Loop over categorized modules, flatten + transform each
    categorized_df_raw = pd.DataFrame(keyword_json.get('categorized_shopping_results', []))
    if categorized_df_raw.empty:
        categorized_df_clean = categorized_df_raw
    else:
        for i in range(len(categorized_df_raw)):
            category_title = categorized_df_raw['title'][i]
            per_category_results_raw = pd.json_normalize(categorized_df_raw['shopping_results'][i])
            per_category_results_clean = transform_results_df(per_category_results_raw,
                                                             raw_id=raw_id, pulled_at=pulled_at, keyword=keyword, page=page,
                                                             module_type='categorized_products', module_label=categorized_df_raw['title'][i], module_index=i+1)
            if i == 0:
                categorized_df_clean = per_category_results_clean.copy()
            else:
                categorized_df_clean = (pd.concat([categorized_df_clean, per_category_results_clean], 
                                            ignore_index=True))
            
    df_list.append(categorized_df_clean)

    #7) (If they exist) Build inline results
    inline_df_raw = pd.DataFrame(keyword_json.get('inline_shopping_results', []))
    if inline_df_raw.empty:
                inline_df_clean = inline_df_raw
    else:
        inline_df_clean = transform_results_df(inline_df_raw, 
                                                raw_id=raw_id, pulled_at=pulled_at, keyword=keyword, page=page,
                                                module_type='inline_products', module_label='Inline products', module_index=100)
    
    df_list.append(inline_df_clean)

    # 8) Return union of uncategorized + categorized (if exists) + inline (if exists) into one df
    return pd.concat(df_list, ignore_index=True)