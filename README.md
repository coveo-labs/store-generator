# Store Generator

## Getting Started

This repo is used to generate store catalogs based upon an image set.

## Steps
### Setup
Create the keys you need and put them in `settings.json`. See for an example of the json to use `settings_EXAMPLE.json`.

### Configuration
Create a file like the `config.json`. It contains:
* global information
 * "fileLocation": were the images will be stored/retrieved
 * "offsetColor": offset area to use when picking a color
 * "offsetHSV": offset area to use applying the HSV mask
 * "GetImagesSkipExistingCategories": In Step 1, when getting the images. Do we want to skip existing Categories?
 * "AWSSkipExisting": In Step 2, if AWS is already in the json, skip the analysis
 * "forceUniqueImageAllCategories": Pexels is reporting an image id, based on that image id we check if we already have the image downloaded. We can do this across all categories
 * "catalogJsonFile": were to store the output json file for the push client
 * "baseUrl": the base url to use for the documentId
 * "baseUrlImages": the base url to use for the images
* category information (this is used for the generation of all content)
 * "searchFor": keyword to search for in Pexels.com
 * "category": Category to use
 * "categoryPath": Path to create in the category facet
 * "useGender": Do genders need to be added
 * "defaultGender": The default gender to use
 * "avgPrice": The average price to use
 * "retailers": Array of random retailers to use
 * "facets": Array of the facets to apply
   * "name": Name to use for the facet. Will be `cat_name` in the JSON to push. So Name: Type will become `cat_type` in the json.
   * "values": Array of random values to use for this facet
   * "default": In the case of a useWhenPropertyValue is not empty the default value to use
   * "variant": Is this facet for a Variant
   * "useWhenPropertyValue": Only apply this facet if one of the `cat_properties` (aka `categories` in the original json from AWS) is found

   ### Steps to perform
   # 1. Determine the keywords to use for the categories. 
   Check on Pexels.com for proper keywords and example images.
   Put those keywords in your config.json

   # 2. Get the images from Pexels.com
   Use: `python 1_getAllPexelImages.py`

   # 3. Goto your image directory and remove any images which are:
   * Not appropiate (Children/Babies/Naked/Weird photos)
   * Do not belong to the category

   # 4. Identify the images using AWS Rekognition
   Use: `python 2_identifyImagesAWS.py`

   # 5. Assign the base colors and pick alternatives (for grouping)
   In order to use grouping we need different colors for different products.
   Use: `python 3_assignColors.py`
   This will open up an image.
   * Click on the image category item to determine the base color. Your command prompt window will show you the color. This area will also be used as a partial image for the previews.
   * When the base color is determined the `image HSV` window is opened. Click here on the item color you want to filter on. Look at windows `option1, option2 and option3` if the proper colors were applied.
   * If you find the colors in one of the option windows appropiate. Simply click on the image -> this will store the window as a 'Child' of the parent.

   # 6. Ready to push the content to your Catalog source
   Use: `python 4_pushToCatalog.py`. 
   This will create a JSON file which you then push against your Catalog source with: `pushapi catalog` (catalog is your directory were you have placed your output files)

