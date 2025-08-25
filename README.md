# Dynamic_Pricing_Engine
Dynamic Pricing Engine will help us get prices based on the Second hand devices conditions and type of accessories included with it

## AI Valuation Layer
This project integrates with the Google Gemini API to provide real-time, AI-powered valuation for submitted devices. The backend service orchestrates the API call, securely manages the API key, and persists the generated offer to the database. The frontend then displays this offer to the user.

### Setup
1.  Obtain a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).
2.  Create a `.env` file in the `backend/` directory (e.g., `backend/.env`).
3.  Add your API key to the `.env` file: `GOOGLE_API_KEY="your-key-here"`.
4.  Rebuild and restart your Docker containers to apply the changes:
    ```bash
    docker-compose up --build -d
    ```

## Seller Decision Flow
This feature allows sellers to accept or decline the AI-generated price offer. Accepting the offer updates the product status to "Pending" for company acquisition, while declining closes the transaction. This completes the initial user journey.

## Internal Acquisition Flow
This feature introduces an internal-facing API endpoint (`POST /api/v1/products/{product_id}/acquire`) to finalize the acquisition of a device. This action transitions the product's status from "Pending" to "In Stock", officially adding it to the company's sellable inventory and completing the procurement phase.

## Dynamic Valuation Engine
This project includes a dynamic valuation engine that adjusts product prices in the inventory based on internal stock levels and sales velocity. A background job (`backend/app/jobs/repricing.py`) runs periodically to reprice "In Stock" items.

### Running the Repricing Job
To manually run the repricing job, execute the following command from your project root:
```bash
docker-compose exec backend python app/jobs/repricing.py
```