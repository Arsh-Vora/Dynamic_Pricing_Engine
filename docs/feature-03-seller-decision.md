### **Feature 3 — Seller's Decision & Status Update**

### 1. Goal

Build the API endpoints and frontend logic required for a user (seller) to either accept or decline the AI-generated price offer. Accepting the offer will transition the product's status to "Pending" for company acquisition, while declining will close the transaction. This feature completes the initial user journey.

### 2. Deliverables

*   `backend/app/api/products.py`: **Updated** with two new endpoints (`/{product_id}/accept` and `/{product_id}/decline`).
*   `frontend/src/components/PriceOfferDisplay.tsx`: A **new** React component to display the offer and handle the user's decision. (We will refactor the offer display out of the main form).
*   `frontend/src/components/ProductSubmissionForm.tsx`: **Updated** to render the new `PriceOfferDisplay` component.
*   `docs/feature-03-seller-decision.md`: This implementation plan.
*   `README.md`: **Updated** with a new "Seller Decision Flow" section.

---

### 3. Scope

#### In

*   **API Endpoints:**
    *   `POST /api/v1/products/{product_id}/accept`: An endpoint to handle the seller's acceptance. It will update the product status from "Registered" to "Pending".
    *   `POST /api/v1/products/{product_id}/decline`: An endpoint to handle the seller's refusal. It will update the product status from "Registered" to "Closed".
*   **Backend Logic:**
    *   CRUD functions to find a product by its ID and update its status.
    *   State validation to ensure a product can only be actioned if its status is "Registered".
*   **Frontend UI:**
    *   The "Yes, I Accept" and "No, Thank You" buttons will be fully functional, calling their respective API endpoints.
*   **Frontend State Management:** The UI will update after a decision is made, showing a clear confirmation or closing message.

#### Out

*   Company-side notifications (e.g., sending an email or Slack message when an offer is accepted). This is planned for Feature 4.
*   Physical acquisition and inspection process logic.
*   User authentication (we are still operating on the assumption of a single, anonymous user flow).

---

### 4. Architecture

This feature introduces state-changing actions initiated by the user after the initial resource has been created. The frontend holds the `productId` received from the valuation step and uses it to make targeted API calls to update the resource's state on the backend. This follows a standard RESTful pattern for modifying existing resources.

```mermaid
flowchart LR
    A[React: Offer Display] -->|User clicks "Accept"| B{POST /api/v1/products/{id}/accept}
    A -->|User clicks "Decline"| C{POST /api/v1/products/{id}/decline}

    subgraph "FastAPI Backend"
        direction LR
        B --> D[Update Product Status Logic]
        C --> D
    end

    D -- "1. Find Product by ID" --> E[PostgreSQL DB]
    E -- "2. Return Product with status 'Registered'" --> D
    D -- "3. UPDATE product SET status = 'Pending'/'Closed'" --> E
    
    subgraph "State Change in DB"
        F["status: 'Registered'"] -- "on Accept" --> G["status: 'Pending'"]
        F -- "on Decline" --> H["status: 'Closed'"]
    end
    
    E -.-> F

    D --> I{API Response (200 OK with updated product)}
    I --> J[React: Confirmation View]
```

---

### 5. Schema Definition

#### Input Schema (API Request)

No new request body schemas are needed. The `product_id` will be passed as a URL path parameter.

#### Output Schema (API Response)

The API endpoints will return the fully updated product object to confirm the state change. We will reuse the existing `ProductResponse` schema from `backend/app/schemas.py`.

| column | type | notes |
| --- | --- | --- |
| `status` | str | **Will now be "Pending" or "Closed"** |
| ... | ... | All other existing product fields |

---

### 6. Implementation Details / Technical Approach

*   **Backend (`backend/app/api/products.py`):**
    *   Create two new `router.post` endpoints. Use path parameters to capture the `product_id`.
    *   **Accept Endpoint (`@router.post("/{product_id}/accept", ...)`):**
        1.  Accept `product_id: int` and the `db: Session` dependency.
        2.  Fetch the product. Raise a `404 Not Found` `HTTPException` if it doesn't exist.
        3.  **State Validation:** Check if `db_product.status == "Registered"`. If not, raise a `400 Bad Request` `HTTPException` with a message like "This offer has already been actioned."
        4.  Update the status: `db_product.status = "Pending"`.
        5.  Commit the change: `db.commit()`, then `db.refresh(db_product)`.
        6.  Return the updated `db_product`.
    *   **Decline Endpoint (`@router.post("/{product_id}/decline", ...)`):**
        1.  Follow the same logic as the accept endpoint, but set the status to `db_product.status = "Closed"`.

*   **Frontend (Refactoring and Logic):**
    1.  **Create `PriceOfferDisplay.tsx`:** Create a new file `frontend/src/components/PriceOfferDisplay.tsx`.
        *   This component will receive the `offer` object (`{ price: number; productId: number; }`) as a prop.
        *   It will manage its own internal state, `decisionMade: 'accepted' | 'declined' | null`.
        *   Create `handleAccept` and `handleDecline` async functions inside this component. These functions will make the `POST` requests to the new endpoints. Upon a successful request, they will update the `decisionMade` state.
        *   The component will use conditional rendering:
            *   If `decisionMade` is `null`, show the offer price and the two buttons.
            *   If `decisionMade` is `'accepted'`, show a success message: "Thank you for your acceptance! We will email you with the next steps for shipping your device."
            *   If `decisionMade` is `'declined'`, show a polite closing message: "Thank you for considering us. Your transaction has been closed."
    2.  **Update `ProductSubmissionForm.tsx`:**
        *   Import your new `PriceOfferDisplay` component.
        *   In the conditional rendering block where you currently show the offer, replace the JSX with your new component:
            ```tsx
            {offer && (
              <PriceOfferDisplay offer={offer} />
            )}
            ```

---

### 7. Error Handling & Edge Cases

*   **Invalid Product ID:** The backend gracefully handles requests for non-existent products by returning a `404 Not Found`.
*   **State Mismatch:** The backend explicitly checks if the product is in the "Registered" state before allowing a status change, preventing invalid operations and returning a `400 Bad Request`. The frontend should disable both buttons after one is clicked to prevent double submissions.

---

### 8. Definition of Done

*   [ ] Two new API endpoints, `/accept` and `/decline`, are implemented and functional in `backend/app/api/products.py`.
*   [ ] The offer display logic is refactored into a new `PriceOfferDisplay.tsx` component.
*   [ ] The frontend component correctly calls the new endpoints and updates its view to a final confirmation message upon success.
*   [ ] The product status in the PostgreSQL database is correctly updated to "Pending" or "Closed".
*   [ ] `README.md` is updated to describe the seller decision flow.
*   [ ] A PR is opened from `feature/3-seller-decision` to `main`.

---

### 9. File Manifest

Files created or modified in this feature:

```
backend/app/api/products.py                      # MODIFIED
frontend/src/components/PriceOfferDisplay.tsx    # CREATED
frontend/src/components/ProductSubmissionForm.tsx  # MODIFIED
docs/feature-03-seller-decision.md             # CREATED
README.md                                        # MODIFIED
```

---

### 10. Conventional Commits

*   `feat(api): create accept and decline offer endpoints`
*   `refactor(frontend): create PriceOfferDisplay component`
*   `feat(frontend): implement seller decision logic and confirmation UI`
*   `docs(readme): add seller decision flow section`

---

### 11. Pull Request Template

**Title:** `feat: implement seller decision flow for offers`

**Summary:**
This PR introduces the complete workflow for a seller to act on a price offer. It adds two new backend endpoints (`/accept` and `/decline`) to handle offer acceptance and refusal, which update the product's status in the database accordingly. State validation is included to prevent invalid transitions.

The frontend has been refactored to use a new `PriceOfferDisplay` component, which encapsulates the logic for calling these new API endpoints. After a user makes a decision, the UI transitions to a final confirmation state. This closes the loop on the initial user interaction.

**Checklist:**
*   [ ] Backend endpoints are implemented and functional.
*   [ ] Frontend logic correctly calls the new endpoints.
*   [ ] Database status updates are verified.
*   [ ] `README.md` has been updated.